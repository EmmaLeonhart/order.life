@echo off
cd /d "%~dp0"

echo ==========================================
echo Launching Claude from repo root:
echo %cd%
echo ==========================================
echo.
start "" /D "%cd%" cmd /k claude
