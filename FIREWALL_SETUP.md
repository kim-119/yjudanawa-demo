# Windows Firewall Configuration Guide for Team DB Access

## Quick Setup (Run as Administrator)

Open PowerShell as Administrator and run:

```powershell
New-NetFirewallRule -DisplayName "PostgreSQL-Ydanawa" -Direction Inbound -Protocol TCP -LocalPort 5433 -Action Allow
```

## Manual Setup (GUI Method)

If you don't have administrator access to PowerShell, follow these steps:

### Method 1: Windows Defender Firewall (Recommended)

1. Press `Win + R` and type `wf.msc`, then press Enter
2. Click "Inbound Rules" on the left panel
3. Click "New Rule..." on the right panel
4. Select "Port" and click "Next"
5. Select "TCP" and enter "5433" in "Specific local ports"
6. Click "Next"
7. Select "Allow the connection" and click "Next"
8. Check all profiles (Domain, Private, Public) and click "Next"
9. Name it "PostgreSQL-Ydanawa" and click "Finish"

### Method 2: Control Panel

1. Open Control Panel
2. Go to "System and Security" > "Windows Defender Firewall"
3. Click "Advanced settings" on the left
4. Follow the same steps as Method 1 from step 2

## Verification

After adding the firewall rule, run the test script:

```powershell
.\test-db-connection.ps1
```

You should see:
- `OK Firewall rule exists`
- All checks should show `OK` status

## Troubleshooting

### If port is still blocked:

1. Check if Windows Firewall is enabled:
   ```powershell
   Get-NetFirewallProfile | Select-Object Name, Enabled
   ```

2. Verify the rule was created:
   ```powershell
   Get-NetFirewallRule -DisplayName "PostgreSQL-Ydanawa"
   ```

3. Check if antivirus software is blocking the port

### If team members still can't connect:

1. Verify your public IP address (if team members are connecting from outside your network)
2. Check router/network firewall settings
3. Consider using port forwarding if behind NAT
4. Test connection from localhost first:
   ```powershell
   # Using Docker exec
   docker exec ydanawa-db psql -U root -d ydanawa_db -c "SELECT version();"
   ```

## Security Note

Opening ports to external networks can be a security risk. Consider:
- Using a VPN for team access
- Restricting access to specific IP addresses
- Using SSL/TLS connections (production)
- Implementing stronger passwords (production)

## For Team Members

Share the following information with your team:

**Connection Details:**
- Host: `<Your_Server_IP>` (172.19.16.1 or 172.33.0.165)
- Port: `5433`
- Database: `ydanawa_db`
- Username: `root`
- Password: `0910`

Refer to `DB_접속_가이드.md` for detailed client setup instructions.

