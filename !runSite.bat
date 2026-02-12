@echo off
cd /d "%~dp0"

echo ==========================================
echo Building site...
echo ==========================================
C:\Users\Immanuelle\AppData\Local\Programs\Python\Python313\python.exe build.py
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Serving site at http://localhost:8000
echo Press Ctrl+C to stop.
echo ==========================================
C:\Users\Immanuelle\AppData\Local\Programs\Python\Python313\python.exe -m http.server 8000 --directory site
