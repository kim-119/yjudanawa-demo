"""Cheetah API 파라미터 테스트"""
import httpx
import asyncio
import json

async def test_cheetah_params():
    client = httpx.AsyncClient(timeout=10.0)
    base_url = "https://lib.yju.ac.kr/Cheetah/api/search"
    isbn = "9788966262281"

    # 다양한 파라미터 조합 시도
    param_combinations = [
        {"keyword": isbn},
        {"query": isbn},
        {"q": isbn},
        {"searchkeyword": isbn},
        {"Searchkeyword": isbn},
        {"SearchValue": isbn},
        {"Keyword": isbn, "SearchType": "total"},
        {"Keyword": isbn, "SearchTarget": "all"},
        {"Keyword": isbn, "CategoryCode": "total"},
    ]

    print("Cheetah API 파라미터 테스트\n" + "="*60)

    for params in param_combinations:
        try:
            response = await client.get(base_url, params=params)
            data = response.json()
            total = data.get("TotalCount", 0)

            if total > 0:
                print(f"\n[SUCCESS] {params}")
                print(f"TotalCount: {total}")
                print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])
            else:
                print(f"[EMPTY] {params} -> TotalCount: {total}")
        except Exception as e:
            print(f"[ERROR] {params} -> {e}")

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_cheetah_params())

