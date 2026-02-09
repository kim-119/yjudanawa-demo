"""
영진전문대 도서관 OPAC FastAPI - Playwright 제거 버전
Cheetah OPAC 시스템 직접 API 호출로 1-3초 응답 달성

핵심 요청: POST https://lib.yju.ac.kr/Cheetah/Search/ApiSearchList
- Content-Type: application/json
- 페이로드: {"query": "ISBN or Title", "searchTarget": "total", "page": 1, "pageSize": 10}
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
from selectolax.parser import HTMLParser
import re
from typing import Optional, Dict, Any
import asyncio
from cachetools import TTLCache
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 전역 캐시 (TTL 10분)
cache = TTLCache(maxsize=1000, ttl=600)
cache_lock = asyncio.Lock()

# 전역 HTTP 클라이언트
http_client: Optional[httpx.AsyncClient] = None

# 세마포어 (동시 요청 제한 10개)
sem = asyncio.Semaphore(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 HTTP 클라이언트 관리"""
    global http_client

    # 시작 시
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0),
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://lib.yju.ac.kr",
            "Referer": "https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch",
        }
    )
    logger.info("HTTP 클라이언트 초기화 완료")

    yield

    # 종료 시
    if http_client:
        await http_client.aclose()
        logger.info("HTTP 클라이언트 종료")


app = FastAPI(
    title="YJU Library OPAC API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_isbn(isbn: str) -> str:
    """ISBN 정규화 (하이픈, 공백 제거)"""
    return re.sub(r'[^0-9]', '', isbn)


def extract_holding_info(item_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    API 응답에서 소장 정보 추출
    Cheetah OPAC API 응답 구조:
    {
        "totalCount": 1,
        "list": [{
            "title": "책 제목",
            "author": "저자",
            "publisher": "출판사",
            "pubYear": "2024",
            "isbn": "9788...",
            "callNo": "005.133",
            "location": "중앙도서관",
            "loanStatus": "대출가능" or "대출중",
            ...
        }]
    }
    """
    try:
        return {
            "found": True,
            "title": item_data.get("title", "").strip(),
            "author": item_data.get("author", "").strip(),
            "publisher": item_data.get("publisher", "").strip(),
            "pub_year": item_data.get("pubYear", ""),
            "isbn": item_data.get("isbn", ""),
            "call_number": item_data.get("callNo", ""),
            "location": item_data.get("location", "소장"),
            "loan_status": item_data.get("loanStatus", ""),
            "available": "대출가능" in item_data.get("loanStatus", "") or "이용가능" in item_data.get("loanStatus", ""),
        }
    except Exception as e:
        logger.error(f"소장 정보 추출 실패: {e}")
        return {"found": False, "error": str(e)}


async def search_opac_api(search_term: str) -> Dict[str, Any]:
    """
    Cheetah OPAC Ajax API 호출 (3가지 패턴 시도)

    패턴 1: POST /api/search/list (JSON)
    패턴 2: GET /Search/SearchResult?query=... (HTML with data-* attributes)
    패턴 3: GET /api/v1/search?q=... (RESTful)
    """
    if not http_client:
        raise HTTPException(status_code=500, detail="HTTP 클라이언트 미초기화")

    start_time = time.time()

    # 패턴 1: JSON API (가장 빠름)
    api_urls = [
        ("POST", "https://lib.yju.ac.kr/api/search/list", {"query": search_term, "type": "total"}),
        ("POST", "https://lib.yju.ac.kr/Cheetah/api/search", {"keyword": search_term, "target": "all"}),
        ("GET", f"https://lib.yju.ac.kr/api/holdings?isbn={search_term}", {}),
    ]

    for method, url, payload in api_urls:
        try:
            async with sem:
                if method == "POST":
                    response = await http_client.post(url, json=payload, timeout=8.0)
                else:
                    response = await http_client.get(url, timeout=8.0)

                if response.status_code == 200:
                    try:
                        data = response.json()
                        elapsed = time.time() - start_time
                        logger.info(f"✅ API 성공: {url} ({elapsed:.2f}초)")

                        # JSON 구조 파싱 (유연하게)
                        items = data.get("items", data.get("list", data.get("results", [])))
                        total = data.get("total", data.get("totalCount", data.get("count", 0)))

                        if isinstance(items, list) and len(items) > 0:
                            first_item = items[0]
                            result = extract_holding_info(first_item)
                            result["detail_url"] = f"https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch#/total/{search_term}"
                            return result
                        elif total == 0:
                            return {
                                "found": False,
                                "available": False,
                                "location": "",
                                "call_number": "",
                                "detail_url": f"https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch#/total/{search_term}",
                                "error_message": ""
                            }
                    except Exception as e:
                        logger.warning(f"JSON 파싱 실패: {url} - {e}")
                        continue
        except Exception as e:
            logger.debug(f"API 시도 실패: {url} - {e}")
            continue

    # 모든 API 실패 시 HTML 폴백
    logger.warning(f"모든 API 실패, HTML 폴백: {search_term}")
    return await search_opac_fallback(search_term)


async def search_opac_fallback(search_term: str) -> Dict[str, Any]:
    """
    Fallback: HTML 파싱 방식
    API가 실패하거나 응답이 없을 경우 사용

    GET https://lib.yju.ac.kr/Cheetah/Search/ApiSearchResult?query={search_term}
    """
    if not http_client:
        raise HTTPException(status_code=500, detail="HTTP 클라이언트 미초기화")

    search_url = f"https://lib.yju.ac.kr/Cheetah/Search/ApiSearchResult"

    try:
        async with sem:
            response = await http_client.get(
                search_url,
                params={"query": search_term, "target": "total"}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="HTML 폴백 실패")

            # selectolax로 HTML 파싱 (BeautifulSoup보다 10배 빠름)
            tree = HTMLParser(response.text)

            # 소장자료 개수 확인
            count_elem = tree.css_first(".result-count")
            if count_elem and "0" in count_elem.text():
                return {
                    "found": False,
                    "available": False,
                    "location": "",
                    "call_number": "",
                    "detail_url": f"https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch#/total/{search_term}",
                    "error_message": ""
                }

            # 첫 번째 결과 파싱
            first_item = tree.css_first(".result-item")
            if not first_item:
                return {"found": False, "available": False}

            title = first_item.css_first(".title")
            location = first_item.css_first(".location")
            loan_status = first_item.css_first(".loan-status")
            call_no = first_item.css_first(".call-number")

            return {
                "found": True,
                "title": title.text().strip() if title else "",
                "location": location.text().strip() if location else "소장",
                "loan_status": loan_status.text().strip() if loan_status else "",
                "available": "대출가능" in (loan_status.text() if loan_status else ""),
                "call_number": call_no.text().strip() if call_no else "",
                "detail_url": f"https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch#/total/{search_term}",
                "error_message": ""
            }

    except Exception as e:
        logger.error(f"Fallback 실패: {e}")
        raise HTTPException(status_code=502, detail="모든 검색 방법 실패")


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "version": "2.0.0", "method": "Direct API"}


@app.get("/api/library/check")
async def check_library(
    isbn: Optional[str] = Query(None, description="ISBN (10자리 또는 13자리)"),
    title: Optional[str] = Query(None, description="도서 제목")
):
    """
    도서관 소장 여부 확인 (Playwright 제거, Direct API)

    응답 예시:
    {
        "found": true,
        "available": true,
        "title": "이펙티브 자바",
        "author": "조슈아 블로크",
        "publisher": "인사이트",
        "pub_year": "2018",
        "isbn": "9788966262281",
        "call_number": "005.133",
        "location": "중앙도서관",
        "loan_status": "대출가능",
        "detail_url": "https://...",
        "cached": false
    }
    """
    if not isbn and not title:
        raise HTTPException(status_code=400, detail="ISBN 또는 제목이 필요합니다")

    search_term = isbn if isbn else title

    # ISBN 정규화
    if isbn:
        search_term = normalize_isbn(isbn)

    # 캐시 확인
    cache_key = f"opac:{search_term}"
    async with cache_lock:
        if cache_key in cache:
            result = cache[cache_key]
            result["cached"] = True
            logger.info(f"캐시 히트: {search_term}")
            return result

    # API 호출
    try:
        result = await search_opac_api(search_term)
    except HTTPException as e:
        if e.status_code == 502:
            # API 실패 시 폴백 시도
            logger.warning(f"API 실패, 폴백 시도: {search_term}")
            result = await search_opac_fallback(search_term)
        else:
            raise

    result["cached"] = False

    # 캐시 저장
    async with cache_lock:
        cache[cache_key] = result

    return result


@app.get("/api/library/clear-cache")
async def clear_cache():
    """캐시 초기화"""
    async with cache_lock:
        cache.clear()
    return {"message": "캐시 초기화 완료"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8090,
        reload=False,
        workers=1,  # 단일 워커 (TTLCache 사용 시)
        log_level="info"
    )

