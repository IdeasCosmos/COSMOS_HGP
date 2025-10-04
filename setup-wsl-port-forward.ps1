# WSL 포트 포워딩 설정 스크립트
# PowerShell을 관리자 권한으로 실행 필요

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  WSL 포트 포워딩 설정" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# WSL IP 주소 가져오기
$wslIp = (wsl hostname -I).Trim().Split()[0]
Write-Host "WSL IP 주소: $wslIp" -ForegroundColor Yellow
Write-Host ""

# 프론트엔드 포트 포워딩 (5173)
Write-Host "[1/2] 프론트엔드 포트 포워딩 설정 중... (5173)" -ForegroundColor Green
netsh interface portproxy delete v4tov4 listenport=5173 listenaddress=0.0.0.0
netsh interface portproxy add v4tov4 listenport=5173 listenaddress=0.0.0.0 connectport=5173 connectaddress=$wslIp
Write-Host "  ✓ 프론트엔드 포트 포워딩 완료" -ForegroundColor Green
Write-Host ""

# 백엔드 포트 포워딩 (5001)
Write-Host "[2/2] 백엔드 포트 포워딩 설정 중... (5001)" -ForegroundColor Green
netsh interface portproxy delete v4tov4 listenport=5001 listenaddress=0.0.0.0
netsh interface portproxy add v4tov4 listenport=5001 listenaddress=0.0.0.0 connectport=5001 connectaddress=$wslIp
Write-Host "  ✓ 백엔드 포트 포워딩 완료" -ForegroundColor Green
Write-Host ""

# 방화벽 규칙 추가
Write-Host "[3/4] 방화벽 규칙 추가 중..." -ForegroundColor Green
netsh advfirewall firewall add rule name="WSL_COSMOS_Frontend" dir=in action=allow protocol=TCP localport=5173
netsh advfirewall firewall add rule name="WSL_COSMOS_Backend" dir=in action=allow protocol=TCP localport=5001
Write-Host "  ✓ 방화벽 규칙 추가 완료" -ForegroundColor Green
Write-Host ""

# 설정 확인
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  설정 완료!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "현재 포트 포워딩 목록:" -ForegroundColor Yellow
netsh interface portproxy show v4tov4
Write-Host ""
Write-Host "브라우저에서 접속:" -ForegroundColor Green
Write-Host "  http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "포트 포워딩 삭제 방법:" -ForegroundColor Yellow
Write-Host "  netsh interface portproxy delete v4tov4 listenport=5173 listenaddress=0.0.0.0" -ForegroundColor Gray
Write-Host "  netsh interface portproxy delete v4tov4 listenport=5001 listenaddress=0.0.0.0" -ForegroundColor Gray
Write-Host ""
pause
