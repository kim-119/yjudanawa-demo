"""
영진전문대 도서관 OPAC FastAPI - 현실적 최종 솔루션
========================================================

결론: Cheetah OPAC은 공개 API가 없음 (모든 엔드포인트 404 또는 TotalCount:0)
해결책: Playwright 최소화 + 강력한 캐시 (Redis/TTL) + 병렬 처리

성능:
- 캐시 히트: <10ms (99%)
- 캐시 미스: 15-30초 (Playwright 불가피)
- 첫 검색 이후 즉시 응답

교체 가이드:
1. 기존 gRPC 서버 → 이 FastAPI로 교체
2. Docker에서 Redis 추가 (선택)
3. 프론트엔드에서 /api/library/check 호출
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import re
from typing import Optional, Dict, Any
import asyncio
from cachetools import TTLCache
import time
import logging
from playwright.async_api import async_playwright, Browser, BrowserContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === 설정 ===
CACHE_TTL = 1800  # 30분 (길게 설정)
CACHE_MAXSIZE = 5000  # 크게 설정
CONCURRENT_LIMIT = 3  # Playwright 동시 실행 제한 (낮게)
PLAYWRIGHT_TIMEOUT = 25000  # 25초

# === 전역 상태 ===
cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
cache_lock = asyncio.Lock()
playwright_browser: Optional[Browser] = None
sem = asyncio.Semaphore(CONCURRENT_LIMIT)
stats = {"total": 0, "cache_hits": 0, "playwright_calls": 0}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 Playwright 브라우저 재사용"""
    global playwright_browser

    # 시작
    pw = await async_playwright().start()
    playwright_browser = await pw.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    )
    logger.info("✅ Playwright 브라우저 시작 (재사용 모드)")

    yield

    # 종료
    if playwright_browser:
        await playwright_browser.close()
        logger.info("🛑 Playwright 브라우저 종료")


app = FastAPI(title="YJU Library OPAC - Optimized", version="2.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


async def scrape_library_fast(search_term: str) -> Dict[str, Any]:
    """
    Playwright 최적화 버전
    - 브라우저 재사용 (매번 launch 안 함)
    - 최소 대기 시간
    - 빠른 파싱
    """
    detail_url = f"https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch#/total/{search_term}"

    try:
        async with sem:  # 동시 실행 제한
            # 새 컨텍스트만 생성 (브라우저는 재사용)
            context = await playwright_browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()

            try:
                logger.info(f"🔍 검색: {search_term}")

                # 페이지 로드 (networkidle 대신 domcontentloaded로 빠르게)
                await page.goto(detail_url, timeout=PLAYWRIGHT_TIMEOUT, wait_until="domcontentloaded")

                # 최소 대기 (2초만)
                await page.wait_for_timeout(2000)

                # 페이지 텍스트 추출
                page_text = await page.inner_text("body")

                # 빠른 파싱
                found = False
                if re.search(r'소장자료\s*(\d+)', page_text):
                    match = re.search(r'소장자료\s*(\d+)', page_text)
                    count = int(match.group(1))
                    found = count > 0
                elif any(kw in page_text for kw in ["대출가능", "대출중", "단행본"]):
                    found = True

                if not found:
                    return {"found": False, "available": False, "location": "", "call_number": "", "detail_url": detail_url}

                # 대출 가능 여부
                available = "대출가능" in page_text or "이용가능" in page_text

                # 위치
                location = "소장"
                for loc in ["제1자료실", "제2자료실", "중앙도서관"]:
                    if loc in page_text:
                        location = loc
                        break

                # 청구기호
                call_match = re.search(r'\b(\d{3}(?:\.\d+)?)\b', page_text)
                call_number = call_match.group(1) if call_match else ""

                return {
                    "found": True,
                    "available": available,
                    "location": location,
                    "call_number": call_number,
                    "detail_url": detail_url
                }

            finally:
                await context.close()  # 컨텍스트만 닫기

    except Exception as e:
        logger.error(f"❌ Playwright 에러: {e}")
        raise HTTPException(status_code=500, detail=f"스크래핑 실패: {str(e)}")


@app.get("/health")
async def health():
    """헬스 체크"""
    cache_hit_rate = (stats["cache_hits"] / max(stats["total"], 1)) * 100
    return {
        "status": "ok",
        "cache_size": len(cache),
        "cache_hit_rate_percent": round(cache_hit_rate, 2),
        "stats": stats
    }


@app.get("/api/library/check")
async def check_library(
    isbn: Optional[str] = Query(None),
    title: Optional[str] = Query(None)
):
    """
    소장 여부 확인

    성능:
    - 캐시 히트: <10ms (대부분)
    - 캐시 미스: 15-30초 (Playwright)

    캐시 전략:
    - TTL: 30분 (자주 변하지 않음)
    - 최대 5000개 (충분함)
    """
    start_time = time.time()
    stats["total"] += 1

    if not isbn and not title:
        raise HTTPException(400, "ISBN 또는 제목 필요")

    search_term = re.sub(r'[^0-9]', '', isbn) if isbn else title
    cache_key = f"lib:{search_term}"

    # 캐시 확인
    async with cache_lock:
        if cache_key in cache:
            stats["cache_hits"] += 1
            result = cache[cache_key].copy()
            result["cached"] = True
            result["response_time_ms"] = int((time.time() - start_time) * 1000)
            logger.info(f"💾 캐시 히트: {search_term} ({result['response_time_ms']}ms)")
            return result

    # Playwright 실행
    stats["playwright_calls"] += 1
    logger.info(f"🎭 Playwright 실행: {search_term}")

    result = await scrape_library_fast(search_term)
    result["cached"] = False
    result["response_time_ms"] = int((time.time() - start_time) * 1000)

    # 캐시 저장
    async with cache_lock:
        cache[cache_key] = result.copy()

    logger.info(f"✅ 완료: {search_term} ({result['response_time_ms']}ms)")

    return result


@app.delete("/api/library/cache")
async def clear_cache():
    """캐시 초기화"""
    async with cache_lock:
        count = len(cache)
        cache.clear()
    return {"message": f"캐시 {count}개 삭제"}


# ====================================================================
# 성능 최적화 요약:
#
# 1. Playwright 브라우저 재사용 (launch 비용 제거)
# 2. 동시 실행 제한 3개 (리소스 보호)
# 3. 캐시 TTL 30분, 최대 5000개
# 4. 최소 대기 시간 (2초만)
# 5. domcontentloaded (networkidle보다 빠름)
#
# 결과:
# - 첫 검색: 15-30초 (Playwright 불가피)
# - 이후 검색: <10ms (캐시)
# - 실사용 시 99% 캐시 히트 예상
# ====================================================================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_final:app", host="0.0.0.0", port=8090, reload=False, workers=1)


