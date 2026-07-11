@echo off
echo.
echo  SkillForge AI — starting server...
echo.

REM Check if uvicorn is available
where uvicorn >nul 2>&1
if errorlevel 1 (
  echo [!] uvicorn not found. Installing dependencies...
  pip install uvicorn[standard] fastapi pydantic pydantic-settings python-dotenv httpx python-jose passlib python-multipart
)

REM Start the server in background and open Chrome
start "" uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

REM Wait 2 seconds for the server to boot
timeout /t 2 /nobreak >nul

REM Open Chrome (try common paths)
set CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist %CHROME% set CHROME="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if not exist %CHROME% set CHROME="C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\chrome.exe"

if exist %CHROME% (
  %CHROME% http://127.0.0.1:8000
) else (
  echo Chrome not found at common paths. Open http://127.0.0.1:8000 manually.
  start http://127.0.0.1:8000
)

echo.
echo  Server running at http://127.0.0.1:8000
echo  Press Ctrl+C in this window to stop.
echo.
