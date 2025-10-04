<#
.SYNOPSIS
    COSMOS WSL 포트 자동 설정 스크립트 (자동 모드)
.DESCRIPTION
    사용자 입력 없이 자동으로 WSL 포트 포워딩 및 방화벽 규칙을 설정합니다.
#>

# 관리자 권한 확인 및 자동 상승
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsManager]::Administrator)) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs -WindowStyle Hidden
    exit
}

# WSL IP 가져오기
$wslIP = wsl hostname -I
$wslIP = $wslIP.Trim().Split()[0]

if ([string]::IsNullOrEmpty($wslIP)) {
    exit 1
}

# 포트 목록
$ports = @(5173, 5174, 5001)

# 기존 포트 포워딩 제거
foreach ($port in $ports) {
    netsh interface portproxy delete v4tov4 listenport=$port listenaddress=0.0.0.0 2>$null | Out-Null
}

# 새 포트 포워딩 추가
foreach ($port in $ports) {
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$wslIP 2>$null | Out-Null
}

# 방화벽 규칙 추가
foreach ($port in $ports) {
    $ruleName = "COSMOS-WSL-Port-$port"
    Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue 2>$null | Out-Null
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow -ErrorAction SilentlyContinue | Out-Null
    New-NetFirewallRule -DisplayName "$ruleName-Out" -Direction Outbound -LocalPort $port -Protocol TCP -Action Allow -ErrorAction SilentlyContinue | Out-Null
}

exit 0
