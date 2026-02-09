"""
영진전문대 도서관 OPAC 리버스 엔지니어링 테스트
실제 네트워크 요청을 캡처하여 최적 API를 찾는 스크립트
"""
import httpx
import asyncio
import json
import re

async def test_opac_endpoints():
    """다양한 엔드포인트 시도"""
    isbn = "9788966262281"  # 이펙티브 자바

    client = httpx.AsyncClient(
        timeout=10.0,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Accept-Language": "ko-KR,ko;q=0.9",
        }
    )

    # 테스트할 엔드포인트들
    tests = [
        # 1. 통합검색 페이지 (초기 HTML)
        ("GET", f"https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch#/total/{isbn}", {}),

        # 2. Cheetah OPAC 표준 API들
        ("GET", f"https://lib.yju.ac.kr/api/search?q={isbn}", {}),
        ("POST", "https://lib.yju.ac.kr/api/search", {"query": isbn, "target": "total"}),
        ("GET", f"https://lib.yju.ac.kr/Cheetah/api/search?keyword={isbn}", {}),

        # 3. 소장 정보 직접 조회
        ("GET", f"https://lib.yju.ac.kr/api/holdings?isbn={isbn}", {}),
        ("GET", f"https://lib.yju.ac.kr/Cheetah/Holdings/GetByIsbn?isbn={isbn}", {}),

        # 4. 검색 결과 페이지
        ("GET", f"https://lib.yju.ac.kr/Cheetah/Search/SearchResult?query={isbn}&target=total", {}),

        # 5. Ajax 통합검색
        ("POST", "https://lib.yju.ac.kr/Cheetah/Search/SearchList", {
            "query": isbn,
            "searchTarget": "total",
            "page": 1,
            "pageSize": 10
        }),
    ]

    print("=" * 80)
    print("영진전문대 도서관 OPAC API 탐색")
    print("=" * 80)

    for i, (method, url, payload) in enumerate(tests, 1):
        print(f"\n[테스트 {i}/{len(tests)}] {method} {url}")
        print(f"Payload: {json.dumps(payload, ensure_ascii=False)}")

        try:
            if method == "POST":
                response = await client.post(url, json=payload)
            else:
                response = await client.get(url)

            print(f"[OK] Status: {response.status_code}")
            print(f"[Type] Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"[Size] Length: {len(response.text)} bytes")

            # JSON 응답 확인
            if 'json' in response.headers.get('content-type', ''):
                try:
                    data = response.json()
                    print(f"[JSON] Keys: {list(data.keys())}")
                    print(f"[JSON] Preview: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
                except:
                    pass

            # HTML 응답 확인
            elif 'html' in response.headers.get('content-type', ''):
                scripts = re.findall(r'<script[^>]*>(.*?)</script>', response.text, re.DOTALL)
                print(f"[HTML] Scripts: {len(scripts)}개")

                # __NEXT_DATA__ 또는 window.__INITIAL_STATE__ 찾기
                for script_content in scripts:
                    if "__NEXT_DATA__" in script_content or "__INITIAL_STATE__" in script_content or "window.SEARCH_DATA" in script_content:
                        print(f"[FOUND] {script_content[:200]}...")
                        break

            # 응답 미리보기
            preview = response.text[:300].replace('\n', ' ')
            print(f"[Preview] {preview}...")

        except Exception as e:
            print(f"[FAIL] {e}")

    await client.aclose()
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_opac_endpoints())

