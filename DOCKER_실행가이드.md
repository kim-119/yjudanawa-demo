# 🐳 Docker Desktop에서 Y-DANAWA 실행하기

## 방법 1: Docker Desktop UI 사용 (가장 쉬움)

1. **Docker Desktop 열기**
   - 화면 왼쪽에서 "Compose file viewer" 확인
   - `com:C:\yjudanawa-damo\com` 보임

2. **프로젝트 폴더에서 우클릭**
   - 또는 프로젝트 선택 후 ▶️ 실행 버튼 클릭

3. **컨테이너 시작 대기**
   - 초록색 표시될 때까지 대기 (약 30초)

4. **브라우저 접속**
   - http://localhost

---

## 방법 2: 명령어 실행

### 🚀 빠른 시작
```
START.bat 더블클릭
```

### 또는 수동 실행
```cmd
cd C:\yjudanawa-damo\com

:: 1. 백엔드 빌드
gradlew.bat bootJar -x test

:: 2. Docker Compose 실행  
docker compose up --build -d

:: 3. 상태 확인
docker compose ps

:: 4. 로그 확인
docker compose logs -f
```

---

## 📊 컨테이너 확인

Docker Desktop의 **Containers** 탭에서 확인:
- ✅ **ydanawa-frontend** (포트 80)
- ✅ **ydanawa-backend** (포트 8080)
- ✅ **ydanawa-db** (포트 5432)

모두 🟢 초록색이면 정상 작동!

---

## 🌐 접속 정보

- **프론트엔드**: http://localhost
- **백엔드 API**: http://localhost:8080/api
- **Swagger**: http://localhost:8080/swagger-ui.html

---

## 🛑 중지 방법

### Docker Desktop UI:
1. Containers 탭
2. 프로젝트 선택
3. 🛑 Stop 버튼

### 명령어:
```cmd
docker compose down
```

---

## 💡 문제 해결

### "The file does not exist" 오류
compose.yaml 파일을 클릭해도 내용이 안 보이는 경우:
→ 정상입니다. 그냥 실행하세요!

### 포트 충돌
```cmd
netstat -ano | findstr :80
netstat -ano | findstr :8080
taskkill /F /PID [프로세스번호]
```

### 완전 초기화
```cmd
docker compose down -v
docker compose up --build -d
```

---

**다음 단계**: START.bat 더블클릭하여 실행!

