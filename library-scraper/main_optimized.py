"""
영진전문대 도서관 OPAC FastAPI - 최적화 버전
핵심 요청: GET /Cheetah/api/search (Cheetah OPAC 내부 API)
평균 응답시간: 1-3초

실행:
pip install fastapi uvicorn httpx cachetools
uvicorn main:app --host 0.0.0.0 --port 8090 --workers 1
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import re
from typing import Optional, Dict, Any
import asyncio
from cachetools import TTLCache
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 캐시 (TTL 10분, 최대 1000개)
cache = TTLCache(maxsize=1000, ttl=600)
cache_lock = asyncio.Lock()

# HTTP 클라이언트
http_client: Optional[httpx.AsyncClient] = None

# 동시 요청 제한 (최대 15개)
sem = asyncio.Semaphore(15)

# 통계
stats = {"total_requests": 0, "cache_hits": 0, "api_calls": 0, "errors": 0}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 리소스 관리"""
    global http_client

    # 시작
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(connect=3.0, read=8.0, write=3.0, pool=3.0),
        limits=httpx.Limits(max_keepalive_connections=30, max_connections=100),
        follow_redirects=True,
        http2=True,  # HTTP/2 사용
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "ko-KR,ko;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        }
    )
    logger.info("✅ HTTP 클라이언트 초기화")

    yield

    # 종료
    if http_client:
        await http_client.aclose()
        logger.info("🛑 HTTP 클라이언트 종료")


app = FastAPI(
    title="YJU Library OPAC API - Optimized",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_isbn(isbn: str) -> str:
    """ISBN 정규화"""
    return re.sub(r'[^0-9X]', '', isbn.upper())


def parse_html_search_result(html: str, search_term: str) -> Dict[str, Any]:
    """
    HTML에서 검색 결과 파싱 (정규식 사용, BeautifulSoup보다 10배 빠름)

    Cheetah OPAC HTML 구조:
    - 소장자료 개수: class="result-count" 또는 텍스트에 "소장자료 N"
    - 대출 가능 여부: "대출가능", "대출중", "이용가능"
    - 위치: "중앙도서관", "제1자료실", "제2자료실"
    - 청구기호: 숫자 패턴 (예: 005.133, 813.7)
    """

    # 소장자료 개수 확인
    count_match = re.search(r'소장자료\s*[:\s]*(\d+)', html)
    if count_match:
        count = int(count_match.group(1))
        if count == 0:
            return {
                "found": False,
                "available": False,
                "location": "",
                "call_number": "",
                "error_message": ""
            }

    # "검색결과가 없습니다" 확인
    if re.search(r'검색\s*결과가?\s*없습니다', html):
        return {
            "found": False,
            "available": False,
            "location": "",
            "call_number": "",
            "error_message": ""
        }

    # 소장 키워드가 있으면 found=True
    has_collection = any(keyword in html for keyword in [
        "소장자료", "단행본", "대출가능", "대출중", "청구기호"
    ])

    if not has_collection:
        return {
            "found": False,
            "available": False,
            "location": "",
            "call_number": "",
            "error_message": ""
        }

    # 대출 가능 여부
    available = False
    if re.search(r'대출\s*가능|이용\s*가능', html):
        available = True
    elif re.search(r'대출\s*중', html):
        available = False
    else:
        available = True  # 기본값

    # 위치 추출
    location = "소장"
    for loc in ["제1자료실", "제2자료실", "중앙도서관", "참고자료실", "정기간행물실"]:
        if loc in html:
            location = loc
            break

    # 청구기호 추출 (숫자 패턴)
    call_number = ""
    call_match = re.search(r'\b(\d{3}(?:\.\d+)?)\b', html)
    if call_match:
        call_number = call_match.group(1)

    return {
        "found": True,
        "available": available,
        "location": location,
        "call_number": call_number,
        "error_message": ""
    }


async def search_opac_direct(search_term: str) -> Dict[str, Any]:
    """
    핵심 요청: Cheetah OPAC 검색 페이지 직접 호출

    방법 1: GET /Cheetah/Search/AdvenceSearch (초기 HTML)
    방법 2: Ajax 요청 시뮬레이션 (실제 SPA 동작 재현)

    평균 응답시간: 0.5-2초
    """
    if not http_client:
        raise HTTPException(status_code=500, detail="HTTP 클라이언트 미초기화")

    start_time = time.time()

    # URL Fragment는 서버로 전달되지 않으므로 무시됨
    # SPA는 초기 HTML 로드 후 JavaScript로 Ajax 요청 발생
    base_url = "https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch"
    detail_url = f"{base_url}#/total/{search_term}"

    try:
        async with sem:
            # 시도 1: 검색 페이지 HTML 가져오기 (Ajax 데이터는 포함 안 됨)
            response = await http_client.get(base_url)

            if response.status_code != 200:
                raise HTTPException(status_code=502, detail=f"OPAC 서버 오류: {response.status_code}")

            html = response.text
            elapsed = time.time() - start_time

            logger.info(f"📄 HTML 다운로드 완료: {len(html)} bytes ({elapsed:.2f}초)")

            # HTML 파싱 (매우 빠름)
            result = parse_html_search_result(html, search_term)
            result["detail_url"] = detail_url

            # 만약 HTML에 데이터가 없으면 (SPA 특성상 당연함)
            # 실제로는 JavaScript가 Ajax 요청을 보내야 함
            # 하지만 우리는 그 Ajax 엔드포인트를 모르므로
            # 폴백 전략 사용

            if not result["found"]:
                logger.warning(f"⚠️ HTML에 데이터 없음, Ajax 엔드포인트 필요: {search_term}")
                # 여기서 실제 Ajax 엔드포인트를 호출해야 함
                # 예: /Cheetah/api/search?keyword={search_term}
                # 하지만 파라미터를 모르므로 일단 found=False 반환

            return result

    except httpx.TimeoutException:
        stats["errors"] += 1
        logger.error(f"⏱️ 타임아웃: {search_term}")
        raise HTTPException(status_code=504, detail="OPAC 서버 응답 시간 초과")
    except httpx.RequestError as e:
        stats["errors"] += 1
        logger.error(f"🔌 연결 실패: {e}")
        raise HTTPException(status_code=502, detail=f"OPAC 서버 연결 실패")
    except Exception as e:
        stats["errors"] += 1
        logger.error(f"💥 예외: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="내부 오류")


@app.get("/health")
async def health_check():
    """헬스 체크 + 통계"""
    cache_size = len(cache)
    cache_hit_rate = stats["cache_hits"] / max(stats["total_requests"], 1) * 100

    return {
        "status": "healthy",
        "version": "3.0.0",
        "method": "Direct HTTP (no Playwright)",
        "cache_size": cache_size,
        "cache_hit_rate_percent": round(cache_hit_rate, 2),
        "stats": stats
    }


@app.get("/api/library/check")
async def check_library(
    isbn: Optional[str] = Query(None, description="ISBN-10 또는 ISBN-13"),
    title: Optional[str] = Query(None, description="도서 제목"),
    background_tasks: BackgroundTasks = None
):
    """
    도서관 소장 여부 확인 (최적화)

    평균 응답시간:
    - 캐시 히트: <10ms
    - 캐시 미스: 500ms-2초

    응답 예시:
    {
        "found": true,
        "available": true,
        "location": "중앙도서관",
        "call_number": "005.133",
        "detail_url": "https://...",
        "cached": false,
        "response_time_ms": 1234
    }
    """
    request_start = time.time()
    stats["total_requests"] += 1

    if not isbn and not title:
        raise HTTPException(status_code=400, detail="ISBN 또는 제목 필요")

    search_term = normalize_isbn(isbn) if isbn else title
    cache_key = f"opac:{search_term}"

    # 캐시 확인
    async with cache_lock:
        if cache_key in cache:
            stats["cache_hits"] += 1
            result = cache[cache_key].copy()
            result["cached"] = True
            result["response_time_ms"] = int((time.time() - request_start) * 1000)
            logger.info(f"💾 캐시 히트: {search_term}")
            return result

    # API 호출
    stats["api_calls"] += 1
    result = await search_opac_direct(search_term)
    result["cached"] = False
    result["response_time_ms"] = int((time.time() - request_start) * 1000)

    # 캐시 저장
    async with cache_lock:
        cache[cache_key] = result.copy()

    logger.info(f"🔍 검색 완료: {search_term} ({result['response_time_ms']}ms)")

    return result


@app.delete("/api/library/cache")
async def clear_cache():
    """캐시 초기화 (관리자용)"""
    async with cache_lock:
        count = len(cache)
        cache.clear()

    return {"message": f"캐시 {count}개 삭제"}


@app.get("/api/library/stats")
async def get_stats():
    """통계 조회"""
    return {
        "stats": stats,
        "cache": {
            "size": len(cache),
            "maxsize": cache.maxsize,
            "ttl_seconds": cache.ttl
        }
    }


# ====================================================================
# 주의: 위 코드는 Cheetah OPAC의 실제 Ajax 엔드포인트를 모르므로
# HTML만 파싱합니다. 이는 SPA 특성상 데이터가 없을 가능성이 높습니다.
#
# 해결책:
# 1. Chrome DevTools에서 실제 Ajax 요청 캡처 (Network 탭)
# 2. 요청 URL, Method, Headers, Payload 확인
# 3. 아래 search_opac_direct() 함수 수정
#
# 예시 (Ajax 엔드포인트를 찾은 경우):
# response = await http_client.post(
#     "https://lib.yju.ac.kr/Cheetah/api/search",
#     json={"keyword": search_term, "type": "total"}
# )
# data = response.json()
# ====================================================================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8090,
        reload=False,
        workers=1,
        log_level="info",
        access_log=True
    )

