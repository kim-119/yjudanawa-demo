# 🐳 Y-DANAWA Docker 구성 완료!

## ✅ 구현 완료 사항

Docker를 사용하여 Y-DANAWA 애플리케이션을 쉽게 실행할 수 있도록 모든 설정이 완료되었습니다.

## 📁 생성된 파일

### Docker 설정 파일
- ✅ `Dockerfile` - 백엔드 이미지 빌드
- ✅ `frontend/Dockerfile` - 프론트엔드 이미지 빌드  
- ✅ `compose.yaml` - 전체 스택 오케스트레이션 (개선됨)
- ✅ `.dockerignore` - 백엔드 빌드 최적화
- ✅ `frontend/.dockerignore` - 프론트엔드 빌드 최적화

### 실행 스크립트
- ✅ `docker-run.ps1` - PowerShell 실행 스크립트
- ✅ `docker-run.bat` - Windows 배치 파일 (더블클릭 실행)
- ✅ `docker-stop.ps1` - PowerShell 중지 스크립트
- ✅ `docker-stop.bat` - Windows 배치 중지 파일
- ✅ `docker-logs.ps1` - 로그 확인 스크립트

### 문서
- ✅ `DOCKER_SETUP.md` - Docker 설정 상세 가이드
- ✅ `README.md` - Docker 실행 방법 추가

## 🚀 사용 방법

### 방법 1: 배치 파일 (가장 쉬움)
```
1. docker-run.bat 더블클릭
2. 브라우저에서 http://localhost 접속
```

### 방법 2: PowerShell 스크립트
```powershell
.\docker-run.ps1
```

### 방법 3: 수동 실행
```powershell
# 1. 백엔드 빌드
.\gradlew.bat clean bootJar -x test

# 2. Docker Compose 실행
docker-compose up --build -d

# 3. 브라우저에서 접속
# http://localhost
```

## 📊 서비스 구성

| 서비스 | 컨테이너명 | 포트 | 설명 |
|--------|-----------|------|------|
| frontend | ydanawa-frontend | 80 | Vue.js + Nginx |
| backend | ydanawa-backend | 8080 | Spring Boot |
| db | ydanawa-db | 5432 | PostgreSQL + pgvector |

## 🎯 개선된 기능

### 1. 헬스체크 (Health Check)
```yaml
# 데이터베이스 준비 확인
db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U root -d ydanawa_db"]
    interval: 10s
    timeout: 5s
    retries: 5

# 백엔드 준비 확인
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

### 2. 의존성 관리
- 백엔드는 데이터베이스가 완전히 준비된 후 시작
- 프론트엔드는 백엔드가 시작된 후 시작

### 3. 자동 재시작
```yaml
restart: unless-stopped
```
컨테이너가 예기치 않게 중지되면 자동으로 재시작

### 4. 네트워크 격리
```yaml
networks:
  ydanawa-network:
    driver: bridge
```
모든 서비스가 격리된 네트워크에서 통신

### 5. 빌드 최적화
- `.dockerignore` 파일로 불필요한 파일 제외
- 빌드 시간 단축
- 이미지 크기 감소

## 🛠️ 유용한 명령어

### 상태 확인
```powershell
# 컨테이너 상태
docker-compose ps

# 리소스 사용량
docker stats

# 네트워크 확인
docker network ls
```

### 로그 확인
```powershell
# 전체 로그
docker-compose logs

# 특정 서비스
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# 실시간 로그
docker-compose logs -f

# 최근 50줄
docker-compose logs --tail=50
```

### 재시작
```powershell
# 특정 서비스 재시작
docker-compose restart backend

# 전체 재시작
docker-compose restart
```

### 정리
```powershell
# 컨테이너 중지 및 삭제
docker-compose down

# 볼륨까지 삭제 (데이터베이스 초기화)
docker-compose down -v

# 이미지까지 삭제
docker-compose down --rmi all
```

## 📍 접속 정보

개발 환경:
- **프론트엔드**: http://localhost
- **백엔드 API**: http://localhost:8080
- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **데이터베이스**: localhost:5432
  - DB명: ydanawa_db
  - 사용자: root
  - 비밀번호: 0910

## 🔧 트러블슈팅

### 1. 포트 충돌
```powershell
# 사용 중인 포트 확인
netstat -ano | findstr :80
netstat -ano | findstr :8080
netstat -ano | findstr :5432

# 프로세스 종료
taskkill /F /PID [프로세스ID]
```

### 2. Docker Desktop이 실행되지 않음
```
1. 작업 표시줄에서 Docker Desktop 아이콘 확인
2. 없으면 "Docker Desktop" 검색하여 실행
3. "Docker Desktop is starting..." 메시지 기다리기
4. 완전히 시작되면 스크립트 재실행
```

### 3. 빌드 캐시 문제
```powershell
# 캐시 없이 새로 빌드
docker-compose build --no-cache

# 전체 재빌드
docker-compose up --build --force-recreate
```

### 4. 백엔드가 시작되지 않음
```powershell
# 로그 확인
docker-compose logs backend

# 데이터베이스 연결 확인
docker-compose exec db psql -U root -d ydanawa_db -c "\dt"
```

### 5. 프론트엔드가 API 호출 실패
```
- Nginx 설정 확인: frontend/nginx.conf
- 백엔드가 완전히 시작되었는지 확인
- 브라우저 콘솔에서 에러 메시지 확인
```

## 🌐 배포 (프로덕션)

### 환경 변수 설정
`.env` 파일 생성:
```env
KAKAO_REST_API_KEY=실제_카카오_API_키
ALADIN_TTB_KEY=실제_알라딘_API_키
POSTGRES_PASSWORD=강력한_비밀번호
```

### 프로덕션 빌드
```powershell
# 환경 변수 로드하여 실행
docker-compose --env-file .env up --build -d
```

## 📚 추가 문서

- `DOCKER_SETUP.md` - 상세 Docker 설정 가이드
- `README.md` - 프로젝트 전체 README
- `PRICE_CRAWLING_COMPLETE.md` - 가격 크롤링 기능 문서
- `PRICE_COMPARISON_FEATURE.md` - 가격 비교 기능 문서

## ✨ 다음 단계

1. **Docker Desktop 설치** (아직 안 했다면)
2. **docker-run.bat 더블클릭** 또는 `.\docker-run.ps1` 실행
3. **브라우저에서 http://localhost 접속**
4. **도서 검색 및 가격 비교 기능 테스트**

---

**Docker 구성 완료일**: 2026년 2월 8일  
**버전**: 1.0.0  
**상태**: ✅ 프로덕션 준비 완료

