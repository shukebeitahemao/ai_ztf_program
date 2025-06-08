# WSL Connection Reset Fix Script
# Run as Administrator

Write-Host "=== WSL Connection Reset Fix Script ===" -ForegroundColor Green

# Check admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "ERROR: Administrator privileges required!" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Admin privileges verified" -ForegroundColor Green

# Check WSL status
Write-Host "`nChecking WSL status..." -ForegroundColor Yellow
try {
    $wslStatus = wsl --status 2>&1
    Write-Host "WSL Status: $wslStatus" -ForegroundColor Cyan
}
catch {
    Write-Host "WSL command failed" -ForegroundColor Red
}

# Fix network issues
Write-Host "`n=== Fix 1: Reset Network Configuration ===" -ForegroundColor Blue
Write-Host "Resetting network configuration..." -ForegroundColor Yellow
try {
    netsh winsock reset
    netsh int ip reset  
    ipconfig /flushdns
    Write-Host "Network reset completed" -ForegroundColor Green
}
catch {
    Write-Host "Network reset failed: $_" -ForegroundColor Red
}

# Enable WSL features
Write-Host "`n=== Fix 2: Enable WSL Features ===" -ForegroundColor Blue
Write-Host "Enabling WSL features..." -ForegroundColor Yellow
try {
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    Write-Host "WSL feature enabled" -ForegroundColor Green
    
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart  
    Write-Host "Virtual Machine Platform enabled" -ForegroundColor Green
}
catch {
    Write-Host "Feature enabling failed: $_" -ForegroundColor Red
}

# Try to install WSL
Write-Host "`n=== Fix 3: Install WSL ===" -ForegroundColor Blue
Write-Host "Attempting to install WSL..." -ForegroundColor Yellow
try {
    $result = wsl --install 2>&1
    Write-Host "Install result: $result" -ForegroundColor Gray
}
catch {
    Write-Host "WSL installation failed: $_" -ForegroundColor Red
}

# Manual download links
Write-Host "`n=== Manual Download Links ===" -ForegroundColor Magenta
Write-Host "If automatic install fails, download manually:" -ForegroundColor White
Write-Host "WSL2 Kernel: https://aka.ms/wsl2kernel" -ForegroundColor Cyan
Write-Host "Ubuntu 22.04: https://aka.ms/wslubuntu2204" -ForegroundColor Cyan

# Restart recommendation
Write-Host "`n=== Restart Required ===" -ForegroundColor Green
$reboot = Read-Host "Restart computer now to complete setup? (y/n)"
if ($reboot -eq 'y' -or $reboot -eq 'Y') {
    Write-Host "Restarting computer in 10 seconds..." -ForegroundColor Yellow
    shutdown /r /t 10
    Write-Host "Press Ctrl+C to cancel restart" -ForegroundColor Red
}
else {
    Write-Host "Please restart manually to complete WSL setup" -ForegroundColor Yellow
}

Write-Host "`nScript completed!" -ForegroundColor Green
pause 