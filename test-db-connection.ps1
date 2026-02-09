# DB Connection Test Script
# Test if team members can access the database

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Ydanawa DB Connection Test" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check server IP
Write-Host "[1] Server IP Address" -ForegroundColor Yellow
$ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -ExpandProperty IPAddress
Write-Host "   Server IP: " -NoNewline
Write-Host ($ipAddresses -join ", ") -ForegroundColor Green
Write-Host ""

# Check Docker container status
Write-Host "[2] Docker Container Status" -ForegroundColor Yellow
$dbContainer = docker ps --filter "name=ydanawa-db" --format "{{.Status}}"
if ($dbContainer) {
    Write-Host "   OK DB Container: " -NoNewline -ForegroundColor Green
    Write-Host $dbContainer -ForegroundColor Green
} else {
    Write-Host "   ERROR DB Container is not running!" -ForegroundColor Red
    Write-Host "   Run: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check port binding
Write-Host "[3] Port Binding Status" -ForegroundColor Yellow
$portBinding = netstat -ano | Select-String ":5433" | Select-String "LISTENING"
if ($portBinding) {
    Write-Host "   OK Port 5433 is open" -ForegroundColor Green
    $portBinding | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }
} else {
    Write-Host "   ERROR Port 5433 is not open!" -ForegroundColor Red
}
Write-Host ""

# DB internal connection test
Write-Host "[4] DB Internal Connection Test" -ForegroundColor Yellow
$dbTest = docker exec ydanawa-db psql -U root -d ydanawa_db -c "SELECT 'Connection OK' as status;" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK DB internal connection successful" -ForegroundColor Green
} else {
    Write-Host "   ERROR DB internal connection failed" -ForegroundColor Red
}
Write-Host ""

# Check firewall rules
Write-Host "[5] Firewall Rule Check" -ForegroundColor Yellow
$firewallRule = Get-NetFirewallRule -DisplayName "PostgreSQL-Ydanawa" -ErrorAction SilentlyContinue
if ($firewallRule) {
    Write-Host "   OK Firewall rule exists" -ForegroundColor Green
    Write-Host "     Rule Name: PostgreSQL-Ydanawa" -ForegroundColor Gray
    Write-Host "     Status: $($firewallRule.Enabled)" -ForegroundColor Gray
} else {
    Write-Host "   WARNING No firewall rule found" -ForegroundColor Yellow
    Write-Host "   Run as Administrator:" -ForegroundColor Yellow
    Write-Host "   New-NetFirewallRule -DisplayName 'PostgreSQL-Ydanawa' -Direction Inbound -Protocol TCP -LocalPort 5433 -Action Allow" -ForegroundColor Cyan
}
Write-Host ""

# Team member connection info
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Team Connection Info" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
foreach ($ip in $ipAddresses) {
    Write-Host "Host: " -NoNewline
    Write-Host $ip -ForegroundColor Green
}
Write-Host "Port: " -NoNewline
Write-Host "5433" -ForegroundColor Green
Write-Host "Database: " -NoNewline
Write-Host "ydanawa_db" -ForegroundColor Green
Write-Host "Username: " -NoNewline
Write-Host "root" -ForegroundColor Green
Write-Host "Password: " -NoNewline
Write-Host "0910" -ForegroundColor Green
Write-Host ""
Write-Host "See 'DB_접속_가이드.md' for more details." -ForegroundColor Yellow
Write-Host ""

