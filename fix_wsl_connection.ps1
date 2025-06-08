# WSL连接重置问题自动修复脚本
# 需要以管理员身份运行

Write-Host "=== WSL连接重置问题修复脚本 ===" -ForegroundColor Green
Write-Host "正在检查当前用户权限..." -ForegroundColor Yellow

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "错误: 需要管理员权限运行此脚本!" -ForegroundColor Red
    Write-Host "请右键点击PowerShell，选择'以管理员身份运行'，然后重新执行此脚本。" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "✓ 管理员权限验证通过" -ForegroundColor Green

# 检查WSL状态
Write-Host "`n正在检查WSL状态..." -ForegroundColor Yellow
try {
    $wslStatus = wsl --status 2>&1
    Write-Host "当前WSL状态: $wslStatus" -ForegroundColor Cyan
}
catch {
    Write-Host "WSL命令执行失败" -ForegroundColor Red
}

# 方案1: 重置网络配置
Write-Host "`n=== 方案1: 重置网络配置 ===" -ForegroundColor Blue
$choice = Read-Host "是否要重置网络配置? 这可能解决连接问题 (y/n)"
if ($choice -eq 'y' -or $choice -eq 'Y') {
    Write-Host "正在重置网络配置..." -ForegroundColor Yellow
    try {
        netsh winsock reset
        netsh int ip reset
        ipconfig /flushdns
        Write-Host "✓ 网络配置重置完成" -ForegroundColor Green
        Write-Host "建议重启计算机后再尝试WSL命令" -ForegroundColor Yellow
    }
    catch {
        Write-Host "网络重置失败: $_" -ForegroundColor Red
    }
}

# 方案2: 启用WSL功能
Write-Host "`n=== 方案2: 启用WSL功能 ===" -ForegroundColor Blue
$choice = Read-Host "是否要启用WSL功能? (y/n)"
if ($choice -eq 'y' -or $choice -eq 'Y') {
    Write-Host "正在启用WSL功能..." -ForegroundColor Yellow
    try {
        # 启用WSL功能
        dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
        Write-Host "✓ WSL功能启用请求已发送" -ForegroundColor Green
        
        # 启用虚拟机平台
        dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
        Write-Host "✓ 虚拟机平台启用请求已发送" -ForegroundColor Green
        
        Write-Host "功能启用完成，需要重启计算机才能生效" -ForegroundColor Yellow
        
    }
    catch {
        Write-Host "功能启用失败: $_" -ForegroundColor Red
    }
}

# 方案3: 尝试强制安装WSL
Write-Host "`n=== 方案3: 尝试安装WSL ===" -ForegroundColor Blue
$choice = Read-Host "是否要尝试安装WSL? (y/n)"
if ($choice -eq 'y' -or $choice -eq 'Y') {
    Write-Host "正在尝试安装WSL..." -ForegroundColor Yellow
    try {
        # 尝试多种安装方法
        Write-Host "方法1: 使用wsl --install" -ForegroundColor Cyan
        $result = wsl --install 2>&1
        Write-Host "结果: $result" -ForegroundColor Gray
        
        if ($result -like "*连接被重置*" -or $result -like "*connection*reset*") {
            Write-Host "连接问题仍然存在，尝试其他方法..." -ForegroundColor Yellow
            
            Write-Host "方法2: 使用wsl --install --no-launch" -ForegroundColor Cyan
            wsl --install --no-launch 2>&1
        }
        
    }
    catch {
        Write-Host "WSL安装失败: $_" -ForegroundColor Red
    }
}

# 提供手动解决方案
Write-Host "`n=== 如果自动修复失败，请手动执行以下步骤 ===" -ForegroundColor Magenta
Write-Host "1. 手动下载WSL更新包:" -ForegroundColor White
Write-Host "   https://aka.ms/wsl2kernel" -ForegroundColor Cyan
Write-Host "2. 下载Ubuntu发行版:" -ForegroundColor White
Write-Host "   https://aka.ms/wslubuntu2204" -ForegroundColor Cyan
Write-Host "3. 或者通过Windows功能面板启用WSL:" -ForegroundColor White
Write-Host "   Win+R → appwiz.cpl → 启用或关闭Windows功能" -ForegroundColor Cyan

# 检查是否需要重启
Write-Host "`n=== 重启建议 ===" -ForegroundColor Green
$reboot = Read-Host "是否现在重启计算机? 重启后WSL功能才能正常工作 (y/n)"
if ($reboot -eq 'y' -or $reboot -eq 'Y') {
    Write-Host "正在重启计算机..." -ForegroundColor Yellow
    shutdown /r /t 10
    Write-Host "计算机将在10秒后重启，按Ctrl+C取消" -ForegroundColor Red
}
else {
    Write-Host "请稍后手动重启计算机以完成WSL配置" -ForegroundColor Yellow
}

Write-Host "`n脚本执行完成!" -ForegroundColor Green
Read-Host "按回车键退出" 