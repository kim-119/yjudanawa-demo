@echo off
echo ========================================
echo PostgreSQL-Ydanawa Firewall Setup
echo ========================================
echo.
echo This script will create a firewall rule to allow
echo external connections to PostgreSQL on port 5433
echo.
echo This requires Administrator privileges!
echo.
pause

powershell -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command \"New-NetFirewallRule -DisplayName ''PostgreSQL-Ydanawa'' -Direction Inbound -Protocol TCP -LocalPort 5433 -Action Allow; Write-Host ''''; Write-Host ''Firewall rule created successfully!'' -ForegroundColor Green; Write-Host ''''; pause\"' -Verb RunAs"

echo.
echo Done! Run test-db-connection.ps1 to verify.
echo.
pause

