# Docker로 애플리케이션 실행하기

## 🐳 Docker Compose로 전체 스택 실행

### 사전 준비
1. Docker Desktop 설치 및 실행 확인
2. 프로젝트 빌드 완료

### 실행 명령어

#### Windows (PowerShell)
```powershell
# 1. 백엔드 빌드 (필수)
.\gradlew.bat clean bootJar -x test

# 2. Docker Compose로 전체 스택 실행
docker-compose up --build

# 또는 백그라운드 실행
docker-compose up --build -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down

# 볼륨까지 삭제 (데이터베이스 초기화)
docker-compose down -v
```

### 서비스 구성

| 서비스 | 포트 | 설명 |
|--------|------|------|
| frontend | 80 | Vue.js 프론트엔드 (Nginx) |
| backend | 8080 | Spring Boot API |
| db | 5432 | PostgreSQL 데이터베이스 |

### 접속 URL
- **프론트엔드**: http://localhost
- **백엔드 API**: http://localhost:8080/api
- **데이터베이스**: localhost:5432

### 환경 변수 설정 (선택)

`.env` 파일 생성:
```env
KAKAO_REST_API_KEY=your_kakao_key
ALADIN_TTB_KEY=your_aladin_key
```

### 트러블슈팅

#### 포트 충돌
```powershell
# 사용 중인 포트 확인
netstat -ano | findstr :80
netstat -ano | findstr :8080
netstat -ano | findstr :5432

# 프로세스 종료
taskkill /F /PID [프로세스ID]
```

#### 빌드 캐시 삭제
```powershell
docker-compose build --no-cache
```

#### 컨테이너 재시작
```powershell
docker-compose restart backend
docker-compose restart frontend
```

### 개발 모드

#### 백엔드만 실행
```powershell
docker-compose up db -d
# 백엔드는 로컬에서 실행
.\gradlew.bat bootRun
```

#### 프론트엔드만 실행
```powershell
docker-compose up backend db -d
# 프론트엔드는 로컬에서 실행
cd frontend
npm run dev
```

## 🚀 빠른 시작

```powershell
# 1단계: 백엔드 빌드
.\gradlew.bat clean bootJar -x test

# 2단계: Docker Compose 실행
docker-compose up --build -d

# 3단계: 로그 확인
docker-compose logs -f backend

# 4단계: 브라우저에서 접속
# http://localhost
```

## 📝 주의사항

1. **백엔드 빌드 필수**: Docker 이미지를 빌드하기 전에 반드시 `bootJar` 실행
2. **포트 확인**: 80, 8080, 5432 포트가 사용 가능한지 확인
3. **Docker Desktop**: Windows에서는 Docker Desktop이 실행 중이어야 함
4. **데이터 영속성**: `docker-compose down -v` 실행 시 데이터베이스 데이터가 삭제됨

