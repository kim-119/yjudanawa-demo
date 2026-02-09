# 팀 DB 접속 설정 체크리스트

이 문서를 사용하여 모든 설정이 올바르게 완료되었는지 확인하세요.

## ✅ 서버 운영자 체크리스트

### 1단계: Docker 설정 확인
- [ ] `compose.yaml` 포트가 `5433:5432`로 설정됨
- [ ] `compose.yaml`에 `listen_addresses=*` 명령어 추가됨
- [ ] `application.yml`이 `localhost:5433/ydanawa_db`로 설정됨

### 2단계: Docker 실행
```powershell
# 기존 컨테이너 중지
docker-compose down

# 새 설정으로 시작
docker-compose up -d

# 상태 확인 (모두 Up/Healthy 상태여야 함)
docker ps
```
- [ ] ydanawa-db 컨테이너가 실행 중
- [ ] ydanawa-backend 컨테이너가 실행 중
- [ ] ydanawa-frontend 컨테이너가 실행 중
- [ ] ydanawa-library-scraper 컨테이너가 실행 중

### 3단계: 포트 바인딩 확인
```powershell
netstat -ano | Select-String ":5433"
```
- [ ] `0.0.0.0:5433` 또는 `[::]:5433`가 LISTENING 상태

### 4단계: DB 연결 테스트
```powershell
docker exec ydanawa-db psql -U root -d ydanawa_db -c "SELECT version();"
```
- [ ] PostgreSQL 버전 정보가 출력됨 (16.x)

### 5단계: 방화벽 설정 ⚠️ 필수!
**방법 A: 자동 스크립트**
```
setup-firewall.bat 더블클릭
```

**방법 B: 수동 명령어**
```powershell
# PowerShell을 관리자 권한으로 실행
New-NetFirewallRule -DisplayName "PostgreSQL-Ydanawa" -Direction Inbound -Protocol TCP -LocalPort 5433 -Action Allow
```

**방법 C: GUI**
1. `Win + R` → `wf.msc`
2. Inbound Rules → New Rule
3. Port → TCP → 5433 → Allow

- [ ] 방화벽 규칙 생성 완료

### 6단계: 최종 테스트
```powershell
.\test-db-connection.ps1
```
- [ ] [1] Server IP 확인됨
- [ ] [2] Docker Container: OK
- [ ] [3] Port Binding: OK
- [ ] [4] DB Connection: OK
- [ ] [5] Firewall Rule: OK

### 7단계: 서버 IP 확인
```powershell
ipconfig | Select-String "IPv4"
```
또는 테스트 스크립트에서 확인한 IP:
- [ ] IP 주소 메모: ___________________

## ✅ 팀원에게 전달할 정보

### 필수 전달 사항
- [ ] **DB_접속_가이드.md** 파일 공유
- [ ] **서버 IP 주소** 알려주기
- [ ] **포트 번호 5433** 강조 (5432 아님!)

### 접속 정보 템플릿 (복사해서 팀원에게 전달)
```
=================================
Ydanawa 프로젝트 DB 접속 정보
=================================

Host: [여기에 서버 IP 입력]
Port: 5433
Database: ydanawa_db
Username: root
Password: 0910

⚠️ 포트가 5433입니다! (기본 5432 아님)

자세한 접속 방법은 'DB_접속_가이드.md' 파일을 참고하세요.
- DBeaver 설정 방법
- IntelliJ DataGrip 설정 방법
- pgAdmin 설정 방법
- Spring Boot 설정 방법

문제가 있으면 말씀해주세요!
```

## ✅ 팀원 체크리스트

### 연결 테스트
클라이언트(DBeaver, IntelliJ 등)로 다음 정보로 연결 시도:

- [ ] Host에 서버 IP 입력
- [ ] Port에 **5433** 입력 (5432 아님!)
- [ ] Database에 **ydanawa_db** 입력
- [ ] Username에 **root** 입력
- [ ] Password에 **0910** 입력
- [ ] Test Connection 성공

### 확인 사항
연결 후 다음 SQL 실행:
```sql
-- 데이터베이스 버전 확인
SELECT version();

-- 테이블 목록 확인
\dt

-- 또는
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- 도서 데이터 확인
SELECT COUNT(*) FROM books;
```

- [ ] PostgreSQL 16.x 버전 확인
- [ ] books, users, user_roles 등 테이블 존재 확인
- [ ] books 테이블에 100개 이상 데이터 확인

## 🔧 문제 해결 체크리스트

### 연결이 안 될 때
- [ ] 서버 IP 주소가 정확한가?
- [ ] 포트 5433을 입력했는가? (5432 아님)
- [ ] 서버의 Docker 컨테이너가 실행 중인가?
- [ ] 서버의 방화벽 규칙이 설정되었는가?
- [ ] 같은 네트워크에 있는가? (학교 내부 vs 외부)

### "Connection refused" 오류
서버에서 확인:
```powershell
# Docker 상태
docker ps

# 포트 상태
netstat -ano | Select-String ":5433"

# 방화벽
Get-NetFirewallRule -DisplayName "PostgreSQL-Ydanawa"
```

### "timeout" 오류
- [ ] 네트워크 연결 확인 (ping)
- [ ] VPN 필요 여부 확인
- [ ] 라우터/공유기 방화벽 확인

### "authentication failed" 오류
- [ ] Username: `root` (소문자)
- [ ] Password: `0910`
- [ ] Database: `ydanawa_db`

## 📚 참고 문서

- **DB_접속_가이드.md** - 상세 접속 방법
- **DB_설정_완료.md** - 전체 설정 요약
- **FIREWALL_SETUP.md** - 방화벽 설정 가이드
- **DB_설정_요약.md** - 빠른 참고 요약

## 🎉 모든 체크 완료!

위의 모든 항목이 체크되었다면 팀 DB 접속 설정이 완료되었습니다!

팀원들이 성공적으로 DB에 접속하면 이 문서를 완료로 표시하세요.

---
**설정 완료 일자**: _________________
**서버 IP**: _________________
**팀원 접속 확인**: [ ] 완료

