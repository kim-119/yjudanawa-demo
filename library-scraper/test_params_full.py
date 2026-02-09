"""Cheetah API 파라미터 전수조사"""
import httpx
import json

isbn = "9788966262281"
base_url = "https://lib.yju.ac.kr/Cheetah/api/search"

params_list = [
    {"keyword": isbn},
    {"Keyword": isbn},
    {"SearchKeyword": isbn},
    {"searchKeyword": isbn},
    {"query": isbn},
    {"Query": isbn},
    {"isbn": isbn},
    {"ISBN": isbn},
    {"keyword": isbn, "type": "total"},
    {"keyword": isbn, "type": "isbn"},
    {"keyword": isbn, "searchType": "isbn"},
    {"keyword": isbn, "categoryCode": "total"},
]

print(f"Testing: {base_url}\n" + "="*70)

for params in params_list:
    try:
        response = httpx.get(base_url, params=params, timeout=5.0)

        if response.status_code == 200:
            data = response.json()
            total = data.get("TotalCount", 0)

            if total > 0:
                print(f"\n✅ SUCCESS: {params}")
                print(f"TotalCount: {total}")
                print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])
                break
            else:
                print(f"❌ Empty: {params}")
        else:
            print(f"⚠️ Error {response.status_code}: {params}")
    except Exception as e:
        print(f"💥 Exception: {params} -> {e}")

print("\n" + "="*70)
print("테스트 완료")

