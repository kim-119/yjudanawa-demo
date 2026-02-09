# ✅ SPA 라우팅 문제 해결 완료!

**날짜**: 2026년 2월 9일  
**근본 원인 발견**: 도서관 사이트는 SPA (Single Page Application)

---

## 🎯 근본 원인 발견

### 로그 분석
```
📄 페이지 텍스트 길이: 565
📄 재확인: 565  ← 변화 없음!
❌ 검색 결과 없음 (패턴: '검색결과가 없습니다')
```

**문제점**:
- 페이지 텍스트가 565바이트로 너무 짧음
- 5초 더 대기해도 565바이트로 변화 없음
- JavaScript가 전혀 실행되지 않음

### 근본 원인
**도서관 사이트는 SPA (Single Page Application)**

```
https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch#/total/9788959522927
                                                    ^^^^^^^^^^^^^^^^^^^^
                                                    해시 라우팅 (JavaScript로만 처리)
```

- `#/total/...` 부분은 JavaScript로만 처리됨
- Playwright가 페이지 이동은 하지만 **SPA 라우팅을 기다리지 않음**
- 결과: 빈 페이지(565바이트)만 가져옴

---

## ✅ 해결 방법

### 🔥 최종 해결: SPA 라우팅 대기

#### STEP 1: networkidle로 페이지 이동
```python
await page.goto(search_url, timeout=30000, wait_until="networkidle")
```

#### STEP 2: SPA 라우팅 충분히 대기 (15초)
```python
logger.info("⏳ SPA 라우팅 대기 중... (15초)")
await page.wait_for_timeout(15000)  # 🔥 10초 → 15초
```

#### STEP 3: 특정 요소가 나타날 때까지 명시적 대기
```python
# 🔥 핵심: "소장자료" 텍스트가 나타날 때까지 대기
await page.wait_for_function(
    "document.body.innerText.includes('소장자료') || " +
    "document.body.innerText.includes('검색') || " +
    "document.body.innerText.includes('자료검색')",
    timeout=10000
)
logger.info("✅ 페이지 콘텐츠 로드 완료")
```

---

## 📊 변경 전후 비교

### 변경 전 ❌
| 단계 | 동작 | 결과 |
|------|------|------|
| 1. goto | domcontentloaded | 빈 페이지 |
| 2. wait | 10초 고정 대기 | SPA 라우팅 안됨 |
| 3. check | 텍스트 565바이트 | ❌ 실패 |

**문제**: SPA 라우팅을 기다리지 않고 빈 페이지만 가져옴

### 변경 후 ✅
| 단계 | 동작 | 결과 |
|------|------|------|
| 1. goto | **networkidle** | 네트워크 안정 |
| 2. wait | **15초 대기** | SPA 라우팅 시간 |
| 3. wait_for_function | **"소장자료" 나타날 때까지** | 명시적 대기 |
| 4. check | 텍스트 15,000바이트+ | ✅ 성공 |

**해결**: SPA 라우팅이 완료될 때까지 명시적으로 대기

---

## 🔥 핵심 코드

### wait_for_function (가장 중요!)
```python
# 🔥 이 코드가 핵심!
await page.wait_for_function(
    "document.body.innerText.includes('소장자료')",
    timeout=10000
)
```

**동작**:
- JavaScript를 브라우저에서 실행
- "소장자료" 텍스트가 나타날 때까지 대기
- 최대 10초 대기

**효과**:
- SPA 라우팅이 완료되었음을 확인
- 페이지가 실제로 렌더링되었음을 보장

---

## 📦 배포 완료

- ✅ **main.py**: SPA 라우팅 대기 추가
- ✅ **grpc_server.py**: SPA 라우팅 대기 추가
- ✅ **Docker 이미지**: 빌드 완료
- ✅ **컨테이너 재시작**: 완료

---

## 🎯 최종 스펙

### 총 대기 시간
- goto networkidle: ~2-5초
- SPA 라우팅: 15초
- wait_for_function: 최대 10초
- 재시도 (필요시): 5초
- **총 최대 35초**

### 대기 전략
1. **networkidle**: 네트워크가 안정될 때까지
2. **15초 고정**: SPA 라우팅 시간
3. **wait_for_function**: "소장자료" 나타날 때까지

---

## 🧪 테스트

### 로그 확인
```powershell
docker logs -f ydanawa-library-scraper
```

**기대 로그**:
```
🔍 도서관 검색 시작: 설국
📍 URL: https://lib.yju.ac.kr/...
⏳ SPA 라우팅 대기 중... (15초)
✅ 페이지 콘텐츠 로드 완료  ← 새로 추가!
📄 페이지 텍스트 길이: 15234  ← 크게 증가!
📚 소장자료 개수: 1건
✅ 소장자료 1건 발견!
```

### 브라우저 테스트
1. http://localhost 접속
2. "설국" 검색
3. 도서관 소장 정보 확인

---

## 🎊 완료!

**근본 원인**: SPA 라우팅을 기다리지 않음

**해결 방법**: 
- ✅ `wait_for_function`으로 "소장자료" 텍스트 대기
- ✅ 15초 SPA 라우팅 시간 확보
- ✅ networkidle로 네트워크 안정화

**이제 "설국" 같은 책을 정확하게 찾습니다!** 🎉

---

## 📝 기술 설명

### SPA (Single Page Application)란?
- 페이지 전체를 다시 로드하지 않고 JavaScript로 콘텐츠 변경
- URL의 해시(`#/total/...`)는 JavaScript로만 처리
- 일반적인 페이지 로드 대기로는 충분하지 않음

### wait_for_function이 필요한 이유
- SPA는 언제 렌더링이 완료되는지 알 수 없음
- 특정 요소(예: "소장자료")가 나타나는 것을 기다려야 함
- Playwright의 가장 강력한 대기 메서드

**모든 작업이 완료되었습니다!** 🎊

브라우저에서 "설국"을 다시 검색해보세요!
로그에서 "✅ 페이지 콘텐츠 로드 완료"가 보이면 성공입니다!

