@echo off
setlocal

echo ============================================================
echo   MKRS - MANUAL CHAT MODE (Starting All Systems)
echo ============================================================
echo.

:: 1. CLEANUP: Kill any lingering background processes to free RAM
echo [1/3] Clearing RAM and killing background tasks...
taskkill /F /FI "WINDOWTITLE eq 1. Frontend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq 2. Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq 3. AI Admin*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq 4. Rasa Action Server*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq 5. Rasa NLU Server*" >nul 2>&1
taskkill /F /IM "rasa.exe" >nul 2>&1
echo ✅ System Cleaned.

:: 2. OPTIMIZATION: Pin CPU for Ollama
echo.
echo [2/3] Pinning CPU Resources for Ollama (NumThreads=8)...
set OLLAMA_NUM_THREADS=8
powershell -Command "Get-Process -Name 'ollama' -ErrorAction SilentlyContinue | ForEach-Object { $_.PriorityClass = 'High'; echo '✅ Ollama priority set to HIGH' }"

:: 3. LAUNCH: Start all servers
echo.
echo [3/3] Launching servers...
.\ai-service\venv\Scripts\python.exe sync_brain.py

start "1. Frontend (UI) on :3000" cmd /k "cd frontend && npm start"
start "2. Backend (API) on :5001" cmd /k "cd backend && node server.js"
start "3. AI Admin Server on :8000" cmd /k "cd ai-service && .\venv\Scripts\activate && python admin_server.py"
start "4. Rasa Action Server on :5055" cmd /k "cd ai-service && .\venv\Scripts\activate && rasa run actions"
start "5. Rasa NLU Server on :5005" cmd /k "cd ai-service && .\venv\Scripts\activate && rasa run --enable-api --cors *"

echo.
echo ============================================================
echo   ALL SERVERS STARTING IN SEPARATE WINDOWS.
echo   You can now chat at: http://localhost:3000
echo ============================================================
timeout /t 5
exit
