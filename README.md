# Y-Danawa

영진전문대학교 도서 통합 검색 플랫폼

> 📖 **전체 프로젝트 문서**: [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md) - 모든 기능, 설정, 문제 해결 방법

> 🔗 **팀 DB 접속**: [DB_접속_가이드.md](./DB_접속_가이드.md) | [DB_설정_완료.md](./DB_설정_완료.md)

## ✨ 주요 기능

### 📚 도서 검색
- **DB 검색**: PostgreSQL에 저장된 도서 데이터
- **외부 API 통합**: 알라딘, 카카오 도서 검색 API
- **자동 데이터 로딩**: 앱 시작 시 100권 이상의 실제 도서 자동 수집

### 💰 가격 비교 (실시간 크롤링)
- **YES24** - 실시간 가격 크롤링
- **알라딘** - 실시간 가격 크롤링
- **교보문고** - 실시간 가격 크롤링
- **인터파크** - 실시간 가격 크롤링
- **최저가 자동 표시** - 다나와 스타일 UI

### 🏫 영진전문대 도서관 소장 여부
- **실시간 확인**: ISBN/제목 기준 도서관 소장 여부 자동 확인
- **대출 가능 여부**: 대출 가능/대출 중 상태 표시
- **소장 위치**: 도서관 내 위치 정보 (가능 시)
- **딥링크**: 도서관 웹사이트 직접 확인 링크

---

## 🐳 Docker로 빠른 시작 (권장)

### 사전 준비
1. [Docker Desktop](https://www.docker.com/products/docker-desktop) 설치 및 실행
2. 프로젝트 클론

### 🚀 한 번에 실행하기

```powershell
# PowerShell에서 실행
.\docker-run.ps1
```

이 스크립트가 자동으로:
- ✅ Docker 설치 확인
- ✅ 백엔드 빌드
- ✅ Docker 이미지 빌드
- ✅ 컨테이너 실행

### 📍 접속 정보
- **프론트엔드**: http://localhost
- **백엔드 API**: http://localhost:8080/api
- **데이터베이스**: localhost:5433 (ydanawa_db)

> 💡 **팀원 DB 접속**: [DB_접속_가이드.md](./DB_접속_가이드.md) 참고

### 🛠️ 유용한 명령어

```powershell
# 로그 확인
.\docker-logs.ps1

# 특정 서비스 로그
.\docker-logs.ps1 -Service backend

# 실시간 로그
.\docker-logs.ps1 -Follow

# 중지
.\docker-stop.ps1

# 중지 + 데이터베이스 삭제
.\docker-stop.ps1 -RemoveVolumes
```

### 🔄 수동 실행

```powershell
# 1. 백엔드 빌드
.\gradlew.bat clean bootJar -x test

# 2. Docker Compose 실행
docker-compose up --build -d

# 3. 로그 확인
docker-compose logs -f

# 4. 중지
docker-compose down
```

---

## 💻 로컬 개발 모드

Docker 없이 로컬에서 개발하려면:

### 1. 데이터베이스만 Docker로 실행
```powershell
docker-compose up db -d
```

### 2. 백엔드 실행
```powershell
.\gradlew.bat bootRun
```

### 3. 프론트엔드 실행
```powershell
cd frontend
npm install
npm run dev
```

---

## 📚 도서 데이터 자동 로딩

애플리케이션 시작 시 **DB에 도서가 10권 미만이면** 자동으로 외부 API에서 실제 도서 데이터를 가져옵니다.

### 지원하는 외부 API:
1. **알라딘 API** (우선)
2. **카카오 도서 검색 API** (대체)

### API 키 설정 (선택사항)

외부 API 키가 없어도 기본 데이터는 사용 가능하지만, **더 많은 도서 데이터**를 원하면 아래 키를 설정하세요:

#### 1) 알라딘 TTB 키 발급
- https://www.aladin.co.kr/ttb/wz_contents.aspx
- 회원가입 → TTB 키 발급 → 무료

#### 2) 카카오 REST API 키 발급
- https://developers.kakao.com/
- 내 애플리케이션 → 앱 추가 → REST API 키 복사

#### 3) 환경변수 설정

**Windows PowerShell**:
```powershell
$env:KAKAO_REST_API_KEY="your-kakao-rest-api-key"
$env:ALADIN_TTB_KEY="your-aladin-ttb-key"
```

**Docker Compose**:
```yaml
# compose.yaml
services:
  backend:
    environment:
      - KAKAO_REST_API_KEY=your-kakao-key
      - ALADIN_TTB_KEY=your-aladin-key
```

**로컬 실행** (application.yml):
```yaml
app:
  external:
    kakao-rest-api-key: your-kakao-key
    aladin-ttb-key: your-aladin-key
```

---

## Run Backend + Frontend Together

```powershell
npm install
npm run dev
```

## Frontend Only

```powershell
cd frontend
npm install
npm run dev
```

## Backend Only

```powershell
.\gradlew.bat bootRun
```

---

## Auth

POST `/api/auth/register`

```json
{
  "username": "admin",
  "password": "admin1234"
}
```

POST `/api/auth/login`

```json
{
  "username": "admin",
  "password": "admin1234"
}
```

Response:

```json
{
  "username": "admin",
  "status": "ok",
  "token": "<jwt>",
  "roles": ["ROLE_USER"]
}
```

### Authenticated Request Example

```
Authorization: Bearer <jwt>
```

## Caching

- DB book search results: 10 min (Caffeine)
- External API search results: 10 min (Caffeine)
- User lookup for login: 10 min (Caffeine)
- Frontend search results: 5 min (in-memory)
