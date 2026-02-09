# 팀 DB 접속 설정 완료 ✅

팀원들이 외부에서 PostgreSQL 데이터베이스에 접속할 수 있도록 설정을 완료했습니다!

## ✨ 변경 사항

### 1. Docker 설정 수정
- **파일**: `compose.yaml`
- **포트**: 5432 → **5433** (로컬 PostgreSQL과 충돌 방지)
- **바인딩**: `0.0.0.0:5433` (모든 네트워크 인터페이스에서 접근 가능)
- **PostgreSQL 설정**: `listen_addresses=*` (모든 연결 허용)

### 2. 애플리케이션 설정 수정
- **파일**: `src/main/resources/application.yml`
- **데이터베이스 이름**: `postgres` → `ydanawa_db`
- **포트**: `5432` → `5433`

### 3. 생성된 파일
- ✅ `DB_접속_가이드.md` - 팀원용 상세 접속 가이드
- ✅ `FIREWALL_SETUP.md` - 방화벽 설정 가이드
- ✅ `test-db-connection.ps1` - DB 연결 테스트 스크립트

## 🚀 서버 운영자가 해야 할 일

### 1. 방화벽 설정 (필수)

**PowerShell을 관리자 권한으로 실행**하고 다음 명령을 실행하세요:

```powershell
New-NetFirewallRule -DisplayName "PostgreSQL-Ydanawa" -Direction Inbound -Protocol TCP -LocalPort 5433 -Action Allow
```

또는 GUI로 설정: `FIREWALL_SETUP.md` 참고

### 2. 연결 테스트

```powershell
.\test-db-connection.ps1
```

모든 항목이 ✅ OK 상태여야 합니다.

### 3. 팀원에게 공유할 정보

```
Host: 172.19.16.1 또는 172.33.0.165 (네트워크에 따라 다름)
Port: 5433
Database: ydanawa_db
Username: root
Password: 0910
```

## 📋 팀원들에게 전달할 것

1. **`DB_접속_가이드.md`** 파일 공유
   - DBeaver, IntelliJ, pgAdmin 등 다양한 클라이언트 접속 방법 포함

2. **서버 IP 주소** 알려주기
   - 현재 확인된 IP: `172.19.16.1` 또는 `172.33.0.165`
   - 팀원이 같은 네트워크에 있는지 확인

3. **포트 번호 강조**: `5433` (기본 5432가 아님!)

## 🔍 현재 상태

### Docker 컨테이너
```
✅ ydanawa-db (PostgreSQL) - Port 5433
✅ ydanawa-backend (Spring Boot) - Port 8080
✅ ydanawa-frontend (Nginx) - Port 80
✅ ydanawa-library-scraper (FastAPI) - Port 8090, 50051
```

### 네트워크 바인딩
```
✅ TCP 0.0.0.0:5433 (모든 IPv4 주소에서 접근 가능)
✅ TCP [::]:5433 (모든 IPv6 주소에서 접근 가능)
```

### 데이터베이스 상태
```
✅ PostgreSQL 16.11 실행 중
✅ 데이터베이스: ydanawa_db
✅ 테이블: books, users, user_roles, search_logs, click_logs
```

## 🔧 문제 해결

### 팀원이 연결할 수 없는 경우

1. **방화벽 확인**
   ```powershell
   Get-NetFirewallRule -DisplayName "PostgreSQL-Ydanawa"
   ```

2. **Docker 상태 확인**
   ```powershell
   docker ps
   ```

3. **포트 확인**
   ```powershell
   netstat -ano | Select-String ":5433"
   ```

4. **로그 확인**
   ```powershell
   docker logs ydanawa-db
   ```

### 로컬 PostgreSQL과 충돌하는 경우

현재 설정은 로컬 PostgreSQL(5432)과 Docker PostgreSQL(5433)을 동시에 사용 가능하도록 되어 있습니다.

만약 로컬 PostgreSQL을 중지하고 싶다면:
```powershell
Stop-Service -Name "postgresql-x64-18"
```

## 📚 추가 문서

- `DB_접속_가이드.md` - 팀원용 상세 접속 가이드
- `FIREWALL_SETUP.md` - 방화벽 설정 상세 가이드
- `DOCKER_실행가이드.md` - Docker 실행 가이드

## ⚠️ 보안 주의사항

현재 설정은 **개발/테스트 환경용**입니다:
- 비밀번호가 단순함 (`0910`)
- 모든 IP에서 접근 가능
- SSL/TLS 미사용

**프로덕션 환경**에서는 반드시:
1. 강력한 비밀번호 사용
2. 특정 IP만 접근 허용 (방화벽 규칙 수정)
3. SSL/TLS 연결 사용
4. 정기적인 백업 설정
5. 환경 변수로 민감 정보 관리

## 🎉 완료!

이제 팀원들이 DB에 접속할 수 있습니다!

테스트를 위해 다음을 실행하세요:
```powershell
.\test-db-connection.ps1
```

문제가 있으면 `FIREWALL_SETUP.md`와 `DB_접속_가이드.md`를 참고하세요.

