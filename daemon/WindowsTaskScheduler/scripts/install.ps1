#Requires -Version 5.1
[CmdletBinding()]
param(
	[string]$ExePath = "",
	[string]$TaskName = "CampusNetworkAutoauth"
)

$ErrorActionPreference = "Stop"
$ScriptDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$SchedulerDir = Split-Path -Parent $ScriptDir
$RepoDir      = Split-Path -Parent (Split-Path -Parent $SchedulerDir)
$TemplatePath = Join-Path $SchedulerDir "task.xml.template"

if (-not (Test-Path $TemplatePath)) {
	Write-Error "Template not found: $TemplatePath"; exit 1
}

if ([string]::IsNullOrWhiteSpace($ExePath)) {
	$ParentDir = Split-Path -Parent $SchedulerDir
	foreach ($dir in @($SchedulerDir, $ParentDir, $RepoDir)) {
		$found = Get-ChildItem -Path $dir -Filter "campus-network-autoauth*.exe" `
					-ErrorAction SilentlyContinue |
				Select-Object -First 1
		if ($found) { $ExePath = $found.FullName; break }
	}
}
if ([string]::IsNullOrWhiteSpace($ExePath) -or -not (Test-Path -LiteralPath $ExePath)) {
	$ExePath = Read-Host "Please enter the full path to campus-network-autoauth.exe"
	if (-not (Test-Path -LiteralPath $ExePath)) { Write-Error "Path does not exist"; exit 1 }
}

$ExePath    = (Resolve-Path -LiteralPath $ExePath).Path
$WorkingDir = Split-Path -Parent $ExePath
$UserSid    = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$Author = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

Write-Host "Will create scheduled task:"
Write-Host "  Name       : $TaskName"
Write-Host "  exe        : $ExePath"
Write-Host "  Working Directory : $WorkingDir"
Write-Host "  User SID   : $UserSid"
Write-Host "  Triggers   : Boot / Logon / SessionUnlock"
Write-Host ""

$xml = Get-Content -Path $TemplatePath -Raw -Encoding UTF8
$xml = $xml -replace '^\s*<\?xml[^>]*\?>', '<?xml version="1.0" encoding="UTF-16"?>'
$xml = $xml.Replace("{{TASK_NAME}}",   $TaskName)
$xml = $xml.Replace("{{USER_SID}}",	$UserSid)
$xml = $xml.Replace("{{AUTHOR}}",	  $Author)
$xml = $xml.Replace("{{EXE_PATH}}",	$ExePath)
$xml = $xml.Replace("{{WORKING_DIR}}", $WorkingDir)

$tempXml = Join-Path $env:TEMP "campus-network-autoauth-task.xml"
$utf16 = New-Object System.Text.UnicodeEncoding($false, $true)
[System.IO.File]::WriteAllText($tempXml, $xml, $utf16)

try {
	$output = & schtasks.exe /Create /XML $tempXml /TN $TaskName /F 2>&1
	if ($LASTEXITCODE -ne 0) {
		Write-Host "Failed to create scheduled task" -ForegroundColor Red
		Write-Host $output -ForegroundColor Red
		exit 1
	}
	Write-Host "Task created successfully: $TaskName" -ForegroundColor Green
	Write-Host "View: schtasks /Query /TN $TaskName /V /FO LIST"
	Write-Host "Run immediately: schtasks /Run /TN $TaskName"
} finally {
	Remove-Item $tempXml -ErrorAction SilentlyContinue
}
