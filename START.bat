@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   🐳 Y-DANAWA Docker 빠른 실행
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 백엔드 빌드 중...
call gradlew.bat bootJar -x test --quiet
if %errorlevel% neq 0 (
    echo ❌ 빌드 실패
    pause
    exit /b 1
)
echo ✅ 빌드 완료
echo.

echo [2/3] Docker Compose 실행 중...
echo.
start /wait cmd /c "docker compose up --build -d 2>&1"

echo.
echo [3/3] 완료!
echo.
echo ========================================
echo   ✅ 실행 완료!
echo ========================================
echo.
echo 📍 접속: http://localhost
echo.
echo 📊 상태: docker compose ps
echo 📋 로그: docker compose logs -f
echo 🛑 중지: docker compose down
echo.

pause

