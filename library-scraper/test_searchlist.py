"""Cheetah API 모든 가능한 엔드포인트 테스트"""
import httpx
import json

isbn = "9788966262281"

endpoints = [
    ("POST", "https://lib.yju.ac.kr/Cheetah/api/SearchList", {"SearchKeyword": isbn, "SearchTarget": "Total"}),
    ("POST", "https://lib.yju.ac.kr/Cheetah/Search/ApiSearchList", {"query": isbn, "target": "total"}),
    ("POST", "https://lib.yju.ac.kr/api/SearchList", {"keyword": isbn}),
    ("GET", f"https://lib.yju.ac.kr/Cheetah/api/search?keyword={isbn}", None),
    ("GET", f"https://lib.yju.ac.kr/Cheetah/Search/api?q={isbn}", None),
]

for method, url, payload in endpoints:
    print(f"\n{'='*70}")
    print(f"{method} {url}")
    if payload:
        print(f"Payload: {json.dumps(payload, ensure_ascii=False)}")

    try:
        if method == "POST":
            response = httpx.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10.0)
        else:
            response = httpx.get(url, timeout=10.0)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON Keys: {list(data.keys())}")
                print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
            except:
                print(f"HTML: {response.text[:300]}")
        else:
            print(f"Error: {response.text[:200]}")

    except Exception as e:
        print(f"Exception: {e}")

