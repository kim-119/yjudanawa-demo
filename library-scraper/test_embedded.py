"""HTML에서 embedded JSON 추출"""
import httpx
import asyncio
import json
import re

async def extract_embedded_data():
    client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)

    # 실제 검색 페이지 URL (Fragment는 서버에 전달되지 않음)
    url = "https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch"

    print("HTML에서 embedded JSON 찾기\n" + "="*60)

    response = await client.get(url)
    html = response.text

    print(f"HTML 길이: {len(html)} bytes\n")

    # 패턴 1: <script> 태그 내 JSON
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"Script 태그 개수: {len(scripts)}\n")

    for i, script in enumerate(scripts):
        # window.SEARCH_DATA 찾기
        if "SEARCH_DATA" in script or "searchData" in script:
            print(f"[Script {i+1}] SEARCH_DATA 발견:")
            print(script[:500])
            print("...")

        # JSON.parse 또는 JSON 객체 찾기
        json_matches = re.findall(r'{[^{}]{50,}}', script)
        if json_matches:
            for j, json_str in enumerate(json_matches[:2]):
                try:
                    data = json.loads(json_str)
                    print(f"\n[Script {i+1}][JSON {j+1}] Valid JSON:")
                    print(json.dumps(data, ensure_ascii=False, indent=2)[:300])
                except:
                    pass

    # 패턴 2: data-* 속성
    data_attrs = re.findall(r'data-[a-z-]+="({.*?})"', html)
    if data_attrs:
        print(f"\n\ndata-* 속성 발견: {len(data_attrs)}개")
        for attr in data_attrs[:3]:
            print(attr[:200])

    # 패턴 3: Angular/React initial state
    for pattern in [r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                   r'window\.__NEXT_DATA__\s*=\s*({.*?});',
                   r'App\.init\((.*?)\)',
                   r'window\.appData\s*=\s*({.*?});']:
        matches = re.findall(pattern, html, re.DOTALL)
        if matches:
            print(f"\n\nPattern '{pattern[:30]}...' 발견:")
            print(matches[0][:500])

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(extract_embedded_data())

