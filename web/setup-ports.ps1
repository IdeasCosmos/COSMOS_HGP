<#
.SYNOPSIS
    COSMOS WSL 포트 자동 설정 스크립트
.DESCRIPTION
    WSL 포트 포워딩 및 방화벽 규칙을 자동으로 설정합니다.
    관리자 권한이 필요하며, 자동으로 권한 요청합니다.
#>

# 관리자 권한 확인 및 자동 상승
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsManager]::Administrator)) {
    Write-Host "🔐 관리자 권한이 필요합니다. 권한 상승 중..." -ForegroundColor Yellow
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🌌 COSMOS WSL 포트 설정 자동화" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# WSL IP 가져오기
Write-Host "[1/4] WSL IP 주소 확인 중..." -ForegroundColor Green
$wslIP = wsl hostname -I
$wslIP = $wslIP.Trim().Split()[0]

if ([string]::IsNullOrEmpty($wslIP)) {
    Write-Host "❌ WSL IP를 찾을 수 없습니다. WSL이 실행 중인지 확인하세요." -ForegroundColor Red
    Read-Host "Enter 키를 눌러 종료하세요"
    exit 1
}

Write-Host "   ✓ WSL IP: $wslIP" -ForegroundColor Gray
Write-Host ""

# 포트 목록
$ports = @(5173, 5174, 5001)

# 기존 포트 포워딩 제거
Write-Host "[2/4] 기존 포트 포워딩 제거 중..." -ForegroundColor Green
foreach ($port in $ports) {
    try {
        netsh interface portproxy delete v4tov4 listenport=$port listenaddress=0.0.0.0 2>$null | Out-Null
        Write-Host "   ✓ 포트 $port 제거" -ForegroundColor Gray
    } catch {
        Write-Host "   - 포트 $port 제거 실패 (이미 없음)" -ForegroundColor DarkGray
    }
}
Write-Host ""

# 새 포트 포워딩 추가
Write-Host "[3/4] 새 포트 포워딩 추가 중..." -ForegroundColor Green
foreach ($port in $ports) {
    try {
        netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$wslIP
        Write-Host "   ✓ 포트 $port → $wslIP`:$port" -ForegroundColor Gray
    } catch {
        Write-Host "   ❌ 포트 $port 추가 실패: $_" -ForegroundColor Red
    }
}
Write-Host ""

# 방화벽 규칙 추가
Write-Host "[4/4] 방화벽 규칙 추가 중..." -ForegroundColor Green
foreach ($port in $ports) {
    $ruleName = "COSMOS-WSL-Port-$port"

    # 기존 규칙 제거
    try {
        Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue 2>$null | Out-Null
    } catch {}

    # 새 규칙 추가 (인바운드)
    try {
        New-NetFirewallRule -DisplayName $ruleName `
            -Direction Inbound `
            -LocalPort $port `
            -Protocol TCP `
            -Action Allow `
            -ErrorAction SilentlyContinue | Out-Null
        Write-Host "   ✓ 방화벽 규칙: $ruleName (인바운드)" -ForegroundColor Gray
    } catch {
        Write-Host "   ❌ 방화벽 규칙 추가 실패: $_" -ForegroundColor Red
    }

    # 새 규칙 추가 (아웃바운드)
    try {
        New-NetFirewallRule -DisplayName "$ruleName-Out" `
            -Direction Outbound `
            -LocalPort $port `
            -Protocol TCP `
            -Action Allow `
            -ErrorAction SilentlyContinue | Out-Null
        Write-Host "   ✓ 방화벽 규칙: $ruleName (아웃바운드)" -ForegroundColor Gray
    } catch {}
}
Write-Host ""

# 현재 포트 포워딩 상태 표시
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  📊 현재 포트 포워딩 상태" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
netsh interface portproxy show v4tov4
Write-Host ""

Write-Host "✅ 모든 설정이 완료되었습니다!" -ForegroundColor Green
Write-Host ""
Write-Host "다음 주소로 접속하세요:" -ForegroundColor Yellow
Write-Host "  • http://localhost:5173" -ForegroundColor White
Write-Host "  • http://localhost:5174" -ForegroundColor White
Write-Host "  • http://localhost:5001 (Backend)" -ForegroundColor White
Write-Host ""

# 자동 종료 방지
Read-Host "Enter 키를 눌러 종료하세요"
