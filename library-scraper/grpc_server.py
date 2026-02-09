# gRPC 서버 구현
import grpc
from concurrent import futures
import logging
import asyncio
from playwright.async_api import async_playwright

# Proto 파일에서 생성된 코드 import
import library_pb2
import library_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LibraryServicer(library_pb2_grpc.LibraryServiceServicer):
    """도서관 검색 gRPC 서비스"""

    def CheckLibrary(self, request, context):
        """도서관 소장 여부 확인"""
        isbn = request.isbn
        title = request.title

        if not isbn and not title:
            return library_pb2.LibraryResponse(
                found=False,
                available=False,
                location="",
                call_number="",
                detail_url="",
                error_message="ISBN or title is required"
            )

        search_term = isbn if isbn else title
        search_url = f"https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch#/total/{search_term}"

        logger.info(f"gRPC CheckLibrary: {search_term}")

        try:
            # 비동기 크롤링을 동기 함수에서 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.scrape_library(search_term, search_url))
            loop.close()
            return result

        except Exception as e:
            logger.error(f"Error in CheckLibrary: {str(e)}")
            return library_pb2.LibraryResponse(
                found=False,
                available=False,
                location="",
                call_number="",
                detail_url=search_url,
                error_message=f"검색 실패: {str(e)}"
            )

    def HealthCheck(self, request, context):
        """건강 체크"""
        return library_pb2.HealthCheckResponse(
            status="healthy",
            version="1.0.0"
        )

    async def scrape_library(self, search_term: str, search_url: str):
        """
        Playwright를 사용한 크롤링
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
                # 🚀 최적화: 도서관 검색
                logger.info(f"🔍 도서관 검색 시작: {search_term}")
                logger.info(f"📍 URL: {search_url}")

                # 🚀 STEP 1: 페이지 이동
                await page.goto(search_url, timeout=30000, wait_until="networkidle")
                logger.info("📍 페이지 이동 완료")

                # 🚀 STEP 2: 초기 대기 (JavaScript 실행 시간 확보)
                await page.wait_for_timeout(3000)
                logger.info("⏳ 3초 대기 완료")

                # 🚀 STEP 3: 실제 콘텐츠 로드 대기 (여러 시도)
                content_loaded = False
                for attempt in range(5):  # 최대 5번 시도
                    try:
                        await page.wait_for_function(
                            """
                            () => {
                                const text = document.body.innerText;
                                // 소장 정보 또는 검색 결과 확인
                                const hasResult = text.includes('소장자료') || 
                                                text.includes('검색결과가 없습니다') ||
                                                text.includes('검색 결과가 없습니다') ||
                                                text.includes('단행본') ||
                                                text.includes('도서') ||
                                                text.includes('대출');
                                const isLongEnough = text.length > 800;
                                return hasResult || isLongEnough;
                            }
                            """,
                            timeout=8000
                        )
                        logger.info(f"✅ 페이지 로드 완료 (시도 {attempt + 1})")
                        content_loaded = True
                        break
                    except:
                        logger.warning(f"⚠️ 로드 실패 시도 {attempt + 1}/5 - 추가 대기")
                        await page.wait_for_timeout(2000)

                if not content_loaded:
                    logger.warning("⚠️ 최종 대기 시간 부여")
                    await page.wait_for_timeout(3000)

                # 🚀 STEP 4: 페이지 텍스트 추출
                await page.wait_for_timeout(1000)  # 추가 안정화 대기
                page_text = await page.inner_text("body")
                logger.info(f"📄 페이지 텍스트 길이: {len(page_text)}")

                # 디버깅: 페이지 텍스트 일부 로깅
                preview = page_text[:500] if len(page_text) > 500 else page_text
                logger.info(f"📝 페이지 미리보기: {preview}")

                # 🚀 최적화 1: "없음" 확인 (매우 신중하게)
                no_result_patterns = [
                    "검색결과가 없습니다",
                    "검색 결과가 없습니다",
                    "결과가 없습니다"
                ]

                # 페이지가 너무 짧으면 로딩 실패로 간주
                if len(page_text) < 800:
                    logger.warning(f"⚠️ 페이지 텍스트가 너무 짧음 ({len(page_text)}자) - 추가 대기")
                    await page.wait_for_timeout(3000)
                    page_text = await page.inner_text("body")
                    logger.info(f"📄 재시도 후 페이지 텍스트 길이: {len(page_text)}")

                # "검색결과가 없습니다"가 명확히 있고, 소장 관련 키워드가 전혀 없을 때만 없음으로 판단
                has_no_result_text = any(pattern in page_text for pattern in no_result_patterns)
                has_collection_keywords = any(keyword in page_text for keyword in [
                    "소장자료", "소장", "단행본", "도서", "대출가능", "대출 가능", "대출중", "대출 중",
                    "이용가능", "이용 가능", "청구기호", "서가", "자료실"
                ])

                if has_no_result_text and not has_collection_keywords:
                    logger.info(f"❌ 검색 결과 없음 확정")
                    await browser.close()
                    return library_pb2.LibraryResponse(
                        found=False,
                        available=False,
                        location="",
                        call_number="",
                        detail_url=search_url,
                        error_message=""
                    )

                # 🚀 최적화 2: 소장 여부 판단 (다양한 방법 시도)
                import re
                found = False  # 🔥 초기화 필수!

                # 방법 1: "소장자료 N건" 패턴
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
                        found = False
                    elif count > 0:
                        logger.info(f"✅ 소장자료 {count}건 발견!")
                        found = True
                else:
                    # 방법 2: "소장자료" 텍스트만 있어도 소장으로 간주
                    if "소장자료" in page_text:
                        logger.info("✅ '소장자료' 키워드 발견")
                        found = True
                    # 방법 3: 대출 관련 키워드가 있으면 소장으로 간주
                    elif any(keyword in page_text for keyword in [
                        "대출가능", "대출 가능", "대출중", "대출 중",
                        "이용가능", "이용 가능", "청구기호", "단행본"
                    ]):
                        logger.info("✅ 대출/소장 키워드 발견 - 소장으로 판단")
                        found = True
                    # 방법 4: 서가/자료실 정보가 있으면 소장으로 간주
                    elif any(keyword in page_text for keyword in [
                        "제1자료실", "제2자료실", "중앙도서관", "참고자료실",
                        "정기간행물실", "서가", "자료실"
                    ]):
                        logger.info("✅ 서가/자료실 정보 발견 - 소장으로 판단")
                        found = True
                    else:
                        # 페이지가 충분히 길면서 "없습니다"가 없으면 소장 가능성
                        if len(page_text) > 1000 and "없습니다" not in page_text:
                            logger.info("✅ 페이지 충분히 길고 '없음' 표시 없음 - 소장으로 판단")
                            found = True
                        else:
                            logger.warning("⚠️ 소장 여부 판단 불가")
                            found = False

                # 최종 판단: found가 False이고 페이지가 너무 짧으면 에러로 간주
                if not found and len(page_text) < 1000:
                    logger.error(f"❌ 페이지 로딩 실패 추정 (길이: {len(page_text)})")
                    await browser.close()
                    return library_pb2.LibraryResponse(
                        found=False,
                        available=False,
                        location="",
                        call_number="",
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

                # 🔥 하드코딩: 위치 추출
                location = ""
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
                    location = "소장"

                logger.info(f"📍 위치: {location}")

                # 🔥 하드코딩: 청구기호 추출
                call_number = ""
                import re
                call_pattern = re.search(r'\d{3}(?:\.\d+)?', page_text)
                if call_pattern:
                    call_number = call_pattern.group(0)
                    logger.info(f"📚 청구기호: {call_number}")

                logger.info(f"🎉 최종 결과: found={found}, available={available}, location={location}")

                await browser.close()

                return library_pb2.LibraryResponse(
                    found=found,
                    available=available,
                    location=location,
                    call_number=call_number,
                    detail_url=search_url,
                    error_message=""
                )

            except Exception as e:
                logger.error(f"❌ 스크래핑 에러: {str(e)}")
                await browser.close()

                return library_pb2.LibraryResponse(
                    found=False,
                    available=False,
                    location="",
                    call_number="",
                    detail_url=search_url,
                    error_message=f"에러: {str(e)}"
                )


def serve():
    """gRPC 서버 시작"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    library_pb2_grpc.add_LibraryServiceServicer_to_server(LibraryServicer(), server)

    # 포트 설정
    port = 50051
    server.add_insecure_port(f'[::]:{port}')

    logger.info(f"gRPC Server started on port {port}")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

