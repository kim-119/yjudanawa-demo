# 팀원용 데이터베이스 접속 가이드

## 📊 DB 접속 정보

팀원들이 외부에서 PostgreSQL 데이터베이스에 접속할 수 있도록 설정을 완료했습니다.

### 접속 정보
- **Host**: `<서버_IP_주소>` (서버 운영자에게 문의)
  - 예시: `172.33.0.165` 또는 공인 IP
- **Port**: `5433` ⚠️ 주의: 기본 포트 5432가 아닌 5433 사용
- **Database**: `ydanawa_db`
- **Username**: `root`
- **Password**: `0910`

### DBeaver 접속 방법
1. DBeaver 실행
2. 새 연결 생성 (Database > New Database Connection)
3. PostgreSQL 선택
3. 아래 정보 입력:
   - Host: 서버 IP 주소
   - Port: 5433
   - Database: ydanawa_db
   - Username: root
   - Password: 0910
5. "Test Connection" 클릭하여 연결 확인
6. "Finish" 클릭

### IntelliJ DataGrip / Database Tool 접속 방법
1. Database 탭 열기
2. "+" 버튼 클릭 > Data Source > PostgreSQL
3. 위 접속 정보 입력
4. "Test Connection" 클릭하여 연결 확인
5. "Apply" 및 "OK" 클릭

### pgAdmin 접속 방법
1. pgAdmin 실행
2. Servers 우클릭 > Create > Server
3. General 탭:
   - Name: Ydanawa Project DB
4. Connection 탭:
   - Host: 서버 IP 주소
   - Port: 5433
   - Maintenance database: ydanawa_db
   - Username: root
   - Password: 0910
5. "Save" 클릭

### 명령줄 접속 (psql)
```bash
psql -h <서버_IP_주소> -p 5433 -U root -d ydanawa_db
# 비밀번호: 0910
```

### Spring Boot application.yml 설정 (백엔드 개발자용)
```yaml
spring:
  datasource:
    url: jdbc:postgresql://<서버_IP_주소>:5433/ydanawa_db
    username: root
    password: 0910
    driver-class-name: org.postgresql.Driver
```

## 🔧 서버 운영자 체크리스트

### Docker 컨테이너 재시작 필요
설정을 적용하려면 Docker 컨테이너를 재시작해야 합니다:

```powershell
# 기존 컨테이너 중지 및 제거
docker-compose down

# 새 설정으로 컨테이너 시작
docker-compose up -d
```

### 방화벽 설정 확인
Windows 방화벽에서 5433 포트를 열어야 합니다:

```powershell
# PowerShell을 관리자 권한으로 실행 후:
New-NetFirewallRule -DisplayName "PostgreSQL-Ydanawa" -Direction Inbound -Protocol TCP -LocalPort 5433 -Action Allow
```

### 연결 확인
```powershell
# Docker 로그 확인
docker logs ydanawa-db

# 연결 테스트
docker exec ydanawa-db psql -U root -d ydanawa_db -c "SELECT version();"
```

## ⚠️ 보안 주의사항

현재 설정은 개발/테스트 환경용입니다. 프로덕션 환경에서는:
1. 강력한 비밀번호 사용
2. 특정 IP만 접근 허용 (방화벽 규칙)
3. SSL/TLS 연결 사용
4. 정기적인 백업 설정

## 🆘 문제 해결

### "Connection refused" 오류
- 서버의 방화벽 설정 확인
- Docker 컨테이너가 실행 중인지 확인: `docker ps`
- 5432 포트가 열려있는지 확인

### "timeout" 오류
- 네트워크 연결 확인
- 서버 IP 주소가 정확한지 확인
- VPN 연결 필요한지 확인

### "authentication failed" 오류
- Username과 Password 재확인
- 대소문자 구분 주의

## 📞 문의
문제가 계속되면 팀 프로젝트 리더나 서버 운영자에게 문의하세요.

