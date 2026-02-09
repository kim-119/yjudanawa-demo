# 영진전문대 도서관 스크래퍼 서비스

Python + Playwright + FastAPI로 구현된 도서관 소장 여부 확인 서비스

## 기능

- 영진전문대 도서관 자동 검색
- ISBN 또는 제목으로 검색
- 소장 여부, 대출 가능 여부, 위치 정보 반환

## 설치 및 실행

### 로컬 실행

```bash
cd library-scraper

# 가상환경 생성
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium

# 실행
python main.py
```

### Docker 실행

```bash
# 이미지 빌드
docker build -t library-scraper .

# 컨테이너 실행
docker run -p 8090:8090 library-scraper
```

## API 사용법

### 건강 체크
```bash
curl http://localhost:8090/health
```

### 도서관 검색 (ISBN)
```bash
curl -X POST http://localhost:8090/check-library \
  -H "Content-Type: application/json" \
  -d '{"isbn": "9788994492001"}'
```

### 도서관 검색 (제목)
```bash
curl -X POST http://localhost:8090/check-library \
  -H "Content-Type: application/json" \
  -d '{"title": "자바의 정석"}'
```

### 응답 예시

```json
{
  "found": true,
  "available": true,
  "location": "중앙도서관",
  "call_number": null,
  "detail_url": "https://lib.yju.ac.kr/Cheetah/Search/AdvenceSearch#/total/9788994492001",
  "error_message": null
}
```

## 환경 변수

없음 (현재는 기본 설정 사용)

## 성능

- 응답 시간: 3-5초
- 동시 요청: 최대 10개 권장

## 주의사항

- Playwright는 리소스를 많이 사용합니다
- 프로덕션에서는 캐싱 권장
- 도서관 사이트 구조 변경 시 수정 필요

