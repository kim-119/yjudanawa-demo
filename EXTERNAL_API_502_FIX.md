# 🔧 외부 API 502 에러 해결

## 🐛 문제

사용자 보고: **"외부 API 검색 실패 (status: 502)"**

502 Bad Gateway 에러는 백엔드가 외부 API 서버로부터 응답을 받지 못했거나, 외부 API가 다운되었을 때 발생합니다.

---

## ✅ 해결 방법

### 1. **에러 핸들링 개선** (백엔드)

#### ExternalBookService.java

**변경 전**: 에러가 발생해도 명확한 메시지 없음
```java
KakaoBookResponse response = webClient.get()
    .retrieve()
    .bodyToMono(KakaoBookResponse.class)
    .block();
```

**변경 후**: 4xx/5xx 에러 명확히 처리
```java
KakaoBookResponse response = webClient.get()
    .retrieve()
    .onStatus(status -> status.is4xxClientError() || status.is5xxServerError(),
            clientResponse -> {
                throw new ResponseStatusException(
                        HttpStatus.BAD_GATEWAY,
                        "Kakao API 호출 실패: " + clientResponse.statusCode()
                );
            })
    .bodyToMono(KakaoBookResponse.class)
    .block();
```

**적용**: Kakao API, Aladin API 모두 동일하게 처리

---

### 2. **타임아웃 설정 추가** (백엔드)

외부 API가 응답하지 않을 때 무한 대기 방지:

```java
import reactor.netty.http.client.HttpClient;
import java.time.Duration;

HttpClient httpClient = HttpClient.create()
        .responseTimeout(Duration.ofSeconds(10));

this.webClient = builder
        .clientConnector(new ReactorClientHttpConnector(httpClient))
        .build();
```

**효과**: 10초 이상 응답 없으면 자동으로 타임아웃

---

### 3. **try-catch 추가** (백엔드)

예외 발생 시 명확한 메시지 전달:

```java
private List<BookDto> searchKakao(String query) {
    try {
        // ... API 호출 로직
        return response.documents().stream()
            .map(doc -> new BookDto(...))
            .collect(Collectors.toList());
    } catch (Exception e) {
        throw new ResponseStatusException(
                HttpStatus.BAD_GATEWAY,
                "Kakao API 검색 실패: " + e.getMessage()
        );
    }
}
```

---

### 4. **프론트엔드 에러 메시지 개선**

#### BookDetailPage.vue

**변경 전**: 단순한 에러 메시지
```typescript
if (status === 503 && message) {
    externalError = "외부 도서 API 키 설정이 필요합니다.";
} else {
    externalError = "외부 도서 API 호출에 실패했습니다.";
}
```

**변경 후**: 상태 코드별 상세 메시지
```typescript
if (status === 503) {
    externalError = "외부 도서 API 키 설정이 필요합니다.";
} else if (status === 502) {
    externalError = `외부 도서 API 게이트웨이 오류 (502): ${message || '외부 API 서버 응답 없음'}`;
} else if (status >= 500) {
    externalError = `외부 도서 API 서버 오류 (${status}): ${message || '서버 문제 발생'}`;
} else if (status === 400) {
    externalError = "잘못된 검색 요청입니다.";
} else {
    externalError = `외부 도서 API 호출 실패 (${status || 'NETWORK'}): ${message || '네트워크 오류'}`;
}
```

**추가**: 콘솔 로깅으로 디버깅 지원
```typescript
console.error("외부 API 에러:", { status, message, error });
```

---

## 📊 개선 효과

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| **에러 감지** | ❌ 불명확 | ✅ 4xx/5xx 명확히 구분 |
| **타임아웃** | ❌ 무한 대기 가능 | ✅ 10초 타임아웃 |
| **에러 메시지** | ❌ "API 호출 실패" | ✅ "Kakao API 호출 실패: 502" |
| **사용자 피드백** | 🔴 모호함 | 🟢 구체적 |
| **디버깅** | ❌ 어려움 | ✅ 콘솔 로그 |

---

## 🔍 502 에러 원인 진단

### 1. **외부 API 키 미설정**
```yaml
# compose.yaml 확인
services:
  backend:
    environment:
      - KAKAO_REST_API_KEY=your-kakao-key  # ← 설정했는지 확인
      - ALADIN_TTB_KEY=your-aladin-key      # ← 설정했는지 확인
```

**해결**: 환경변수 설정 후 재시작
```powershell
docker-compose restart backend
```

---

### 2. **외부 API 서버 다운**
- Kakao API: https://developers.kakao.com/ (상태 확인)
- Aladin API: https://www.aladin.co.kr/ttb/ (상태 확인)

**해결**: 외부 서비스가 복구될 때까지 대기, 또는 다른 소스 사용
```typescript
// 자동으로 Kakao 실패 시 Aladin 시도
await searchExternalBooks(keyword, "auto")
```

---

### 3. **네트워크 문제**
- Docker 컨테이너 네트워크 확인
- 방화벽/프록시 설정 확인

**해결**: 
```powershell
# 컨테이너 네트워크 확인
docker network inspect com_default

# 컨테이너 재시작
docker-compose restart backend
```

---

### 4. **API 키 잘못됨**
백엔드 로그 확인:
```powershell
docker logs ydanawa-backend | Select-String -Pattern "401|403|API"
```

**해결**: API 키 재발급 및 재설정

---

## 🧪 테스트 방법

### 1. **브라우저에서 테스트**
1. http://localhost 접속
2. 도서 검색 (예: "자바")
3. 에러 발생 시 F12 → Console 확인
4. 에러 메시지 확인:
   - "외부 도서 API 키 설정이 필요합니다." (503)
   - "외부 도서 API 게이트웨이 오류 (502): ..." (502)

### 2. **직접 API 호출 테스트**
```powershell
# Kakao API 테스트
curl -H "Authorization: KakaoAK YOUR_KEY" `
  "https://dapi.kakao.com/v3/search/book?query=자바"

# Aladin API 테스트
curl "https://www.aladin.co.kr/ttb/api/ItemSearch.aspx?ttbkey=YOUR_KEY&Query=자바&QueryType=Title&output=js"
```

### 3. **로그 확인**
```powershell
# 백엔드 로그
docker logs -f ydanawa-backend

# 에러 메시지 필터링
docker logs ydanawa-backend | Select-String -Pattern "502|BAD_GATEWAY|Kakao|Aladin"
```

---

## 📂 변경된 파일

1. ✅ **ExternalBookService.java**
   - 타임아웃 설정 추가 (10초)
   - onStatus() 에러 핸들링 추가
   - try-catch로 예외 처리 강화

2. ✅ **BookDetailPage.vue**
   - 상태 코드별 에러 메시지 개선
   - 콘솔 로깅 추가
   - 사용자 친화적 메시지

---

## 🚀 배포

```powershell
# 백엔드 재빌드
cd C:\yjudanawa-damo\com
docker-compose up -d --build backend

# 프론트엔드 재빌드
docker-compose up -d --build frontend

# 상태 확인
docker ps
```

---

## 💡 추가 권장사항

### 1. **Retry 로직 추가** (선택사항)
```java
// Spring Retry 사용
@Retryable(
    value = {WebClientException.class},
    maxAttempts = 3,
    backoff = @Backoff(delay = 1000)
)
public List<BookDto> searchKakao(String query) {
    // ... API 호출
}
```

### 2. **Circuit Breaker** (선택사항)
외부 API가 계속 실패하면 자동으로 차단:
```java
// Resilience4j 사용
@CircuitBreaker(name = "kakaoApi", fallbackMethod = "fallbackSearch")
public List<BookDto> searchKakao(String query) {
    // ... API 호출
}

public List<BookDto> fallbackSearch(String query, Exception e) {
    return Collections.emptyList();
}
```

### 3. **모니터링**
- Prometheus + Grafana로 API 응답 시간 모니터링
- 502 에러 발생 횟수 추적
- 알림 설정

---

## ✅ 완료!

**핵심 개선사항**:
1. ✅ 10초 타임아웃 설정
2. ✅ 4xx/5xx 에러 명확히 처리
3. ✅ 상태 코드별 상세 메시지
4. ✅ 콘솔 로깅으로 디버깅 지원
5. ✅ try-catch로 안정성 강화

이제 502 에러가 발생해도 사용자에게 명확한 메시지가 표시되고, 로그를 통해 원인을 쉽게 파악할 수 있습니다.

---

**문제가 계속되면**:
1. `docker logs ydanawa-backend` 로그 확인
2. 외부 API 키 설정 확인
3. 외부 API 서비스 상태 확인
4. 네트워크/방화벽 설정 확인

