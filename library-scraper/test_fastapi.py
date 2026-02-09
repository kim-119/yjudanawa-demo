"""FastAPI 테스트 클라이언트"""
import httpx
import time

base_url = "http://localhost:8090"

# 헬스 체크
try:
    response = httpx.get(f"{base_url}/health", timeout=5.0)
    print(f"Health: {response.status_code}")
    print(response.json())
except Exception as e:
    print(f"Health check failed: {e}")

# 검색 테스트
try:
    isbn = "9788966262281"
    start = time.time()

    response = httpx.get(
        f"{base_url}/api/library/check",
        params={"isbn": isbn},
        timeout=60.0
    )

    elapsed = time.time() - start
    print(f"\n검색 결과 ({elapsed:.2f}초):")
    print(response.json())
except Exception as e:
    print(f"Search failed: {e}")

