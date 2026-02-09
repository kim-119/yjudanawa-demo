# 영진전문대 도서관 스크래핑 서비스
# Python + Playwright + FastAPI

from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
from pydantic import BaseModel
import asyncio
import logging
from typing import Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="YJU Library Scraper")


class LibraryCheckRequest(BaseModel):
    isbn: Optional[str] = None
    title: Optional[str] = None


class LibraryCheckResponse(BaseModel):
    found: bool
    available: bool
    location: Optional[str] = None
    call_number: Optional[str] = None
    detail_url: str
    error_message: Optional[str] = None


@app.get("/")
async def root():
    return {"status": "YJU Library Scraper is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/check-library", response_model=LibraryCheckResponse)
async def check_library(request: LibraryCheckRequest):
    """
    영진전문대 도서관 소장 여부 확인
    """
    if not request.isbn and not request.title:
        raise HTTPException(status_code=400, detail="ISBN or title is required")

    search_term = request.isbn if request.isbn else request.title
    search_url = f"https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch#/total/{search_term}"

    logger.info(f"Checking library for: {search_term}")

    try:
        result = await scrape_library(search_term, search_url)
        return result
    except Exception as e:
        logger.error(f"Error scraping library: {str(e)}")
        return LibraryCheckResponse(
            found=False,
            available=False,
            location=None,
            call_number=None,
            detail_url=search_url,
            error_message=f"검색 실패: {str(e)}"
        )


async def scrape_library(search_term: str, search_url: str) -> LibraryCheckResponse:
    """
    Playwright를 사용하여 도서관 검색 결과 스크래핑
    🔥 하드코딩: 영진전문대 도서관 실제 구조에 맞게 최적화
    """
    async with async_playwright() as p:
        # 🔥 하드코딩: 브라우저 옵션 최적화
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()

        try:
            # 🔥 최적화: 도서관 검색 페이지로 이동
            logger.info(f"🔍 도서관 검색 시작: {search_term}")
            logger.info(f"📍 URL: {search_url}")

            # 🚀 STEP 1: 페이지 이동 (networkidle로 빠르게)
            await page.goto(search_url, timeout=20000, wait_until="networkidle")

            # 🚀 STEP 2: 실제 콘텐츠가 로드될 때까지 대기 (더 엄격한 조건)
            try:
                await page.wait_for_function(
                    """
                    () => {
                        const text = document.body.innerText;
                        const hasContent = text.includes('소장자료') || 
                                         text.includes('검색결과가 없습니다') ||
                                         text.includes('검색 결과가 없습니다');
                        const isLongEnough = text.length > 1000;
                        return hasContent && isLongEnough;
                    }
                    """,
                    timeout=10000
                )
                logger.info("✅ 페이지 로드 완료")
            except:
                logger.warning("⚠️ 타임아웃 - 페이지가 짧을 수 있음")
                # 타임아웃되어도 계속 진행 (추가 대기)
                await page.wait_for_timeout(3000)  # 3초 더

            # 🔥 하드코딩: 페이지 스크린샷 (디버깅용)
            # await page.screenshot(path=f"debug_{search_term}.png")

            # 🚀 최적화: 페이지 텍스트 가져오기 (재시도 제거)
            page_text = await page.inner_text("body")
            logger.info(f"📄 페이지 텍스트 길이: {len(page_text)}")

            # 🚀 최적화 1: "검색 결과 없음" 여러 패턴으로 빠르게 확인
            no_result_patterns = [
                "검색결과가 없습니다",
                "검색 결과가 없습니다",
                "결과가 없습니다",
                "0 건",
                "0건"
            ]

            for pattern in no_result_patterns:
                if pattern in page_text:
                    logger.info(f"❌ 검색 결과 없음 (패턴: '{pattern}')")
                    await browser.close()
                    return LibraryCheckResponse(
                        found=False,
                        available=False,
                        location=None,
                        call_number=None,
                        detail_url=search_url,
                        error_message=None
                    )

            # 🚀 최적화 2: "소장자료 N" 패턴을 여러 방법으로 빠르게 추출
            import re

            collection_match = re.search(r'소장자료\s*(\d+)', page_text)
            if not collection_match:
                collection_match = re.search(r'소장\s*(\d+)', page_text)
            if not collection_match:
                collection_match = re.search(r'(\d+)\s*건', page_text)

            if collection_match:
                count = int(collection_match.group(1))
                logger.info(f"📚 소장자료 개수: {count}건")

                if count == 0:
                    logger.info("❌ 소장자료 0건")
                    await browser.close()
                    return LibraryCheckResponse(
                        found=False,
                        available=False,
                        location=None,
                        call_number=None,
                        detail_url=search_url,
                        error_message=None
                    )
                elif count > 0:
                    logger.info(f"✅ 소장자료 {count}건 발견!")
                    found = True
            else:
                # 🚀 최적화 3: 패턴 없고 페이지 짧으면 빠르게 없음 판단
                logger.warning("⚠️ 소장자료 패턴 없음")
                if len(page_text) < 1500:
                    logger.info("❌ 페이지 짧고 패턴 없음 - 없음")
                    await browser.close()
                    return LibraryCheckResponse(
                        found=False,
                        available=False,
                        location=None,
                        call_number=None,
                        detail_url=search_url,
                        error_message="페이지 로딩 실패"
                    )

            # 🔥 하드코딩: 대출 가능 여부 확인
            available = False
            if "대출가능" in page_text or "대출 가능" in page_text:
                available = True
                logger.info("✅ 대출 가능")
            elif "대출중" in page_text or "대출 중" in page_text:
                available = False
                logger.info("❌ 대출 중")
            elif "이용가능" in page_text or "이용 가능" in page_text:
                available = True
                logger.info("✅ 이용 가능")
            else:
                # 기본값: 있으면 대출 가능으로 가정
                available = True
                logger.info("ℹ️ 대출 상태 불명 - 가능으로 가정")

            # 🔥 하드코딩: 위치 추출 (더 정확하게)
            location = None
            if "제1자료실" in page_text or "제 1 자료실" in page_text:
                location = "제1자료실"
            elif "제2자료실" in page_text or "제 2 자료실" in page_text:
                location = "제2자료실"
            elif "중앙도서관" in page_text:
                location = "중앙도서관"
            elif "참고자료실" in page_text:
                location = "참고자료실"
            elif "정기간행물실" in page_text:
                location = "정기간행물실"
            else:
                location = "소장"  # 기본값

            logger.info(f"📍 위치: {location}")

            # 🔥 하드코딩: 청구기호 추출 시도
            call_number = None
            # 청구기호 패턴: 숫자.숫자 형식
            import re
            call_pattern = re.search(r'\d{3}(?:\.\d+)?', page_text)
            if call_pattern:
                call_number = call_pattern.group(0)
                logger.info(f"📚 청구기호: {call_number}")

            logger.info(f"🎉 최종 결과: found={found}, available={available}, location={location}")

            await browser.close()

            return LibraryCheckResponse(
                found=found,
                available=available,
                location=location,
                call_number=call_number,
                detail_url=search_url,
                error_message=None
            )

        except Exception as e:
            logger.error(f"❌ 스크래핑 에러: {str(e)}")
            await browser.close()

            # 🔥 하드코딩: 에러 발생 시에도 URL은 반환
            return LibraryCheckResponse(
                found=False,
                available=False,
                location=None,
                call_number=None,
                detail_url=search_url,
                error_message=f"에러: {str(e)}"
            )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090, log_level="info")

