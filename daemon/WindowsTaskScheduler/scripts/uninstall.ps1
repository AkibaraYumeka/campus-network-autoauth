#Requires -Version 5.1
param([string]$TaskName = "CampusNetworkAutoauth")
$ErrorActionPreference = "Stop"
$output = & schtasks.exe /Delete /TN $TaskName /F 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to delete task $TaskName. It may not be installed, or the shell may lack elevation." -ForegroundColor Yellow
    Write-Host "Try running uninstall.bat as administrator." -ForegroundColor Yellow
    Write-Host ""
    Write-Host $output -ForegroundColor Yellow
    exit 0
}
Write-Host "Task deleted successfully: $TaskName" -ForegroundColor Green
