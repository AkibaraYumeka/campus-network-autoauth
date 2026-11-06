@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\uninstall.ps1" %*
set "RC=%ERRORLEVEL%"

if "%~1"=="" pause

exit /b %RC%
