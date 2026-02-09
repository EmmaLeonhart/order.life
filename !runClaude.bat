@echo off
cd /d "%~dp0"

echo ==========================================
echo Launching Claude from repo root:
echo %cd%
echo ==========================================
echo.
start "" cmd /k "cd /d ""%cd%"" ^&^& claude"
