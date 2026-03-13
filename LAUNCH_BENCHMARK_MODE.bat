@echo off
setlocal

echo ============================================================
echo   MKRS - AUTOMATIC TESTING MODE (Benchmark/MBS)
echo ============================================================
echo.

:: 1. CRITICAL CLEANUP: Shutdown ALL Chat Servers to free up RAM
echo [1/2] SHUTTING DOWN CHAT SERVERS (Freeing 10GB+ RAM)...
taskkill /F /FI "WINDOWTITLE eq 1. Frontend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq 2. Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq 3. AI Admin*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq 4. Rasa Action Server*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq 5. Rasa NLU Server*" >nul 2>&1
taskkill /F /IM "rasa.exe" >nul 2>&1
echo ✅ Memory Freed.

:: 2. RUN BENCHMARK
echo.
echo [2/2] STARTING THE MBS BENCHMARK TEST...
cd ai-service
call .\venv\Scripts\activate
python eval_v1.py --name "Optimized Brain Run"
cd ..

echo.
echo ============================================================
echo   BENCHMARK COMPLETE.
echo   Results saved in MBS/ directory.
echo   To return to chatting, run 'LAUNCH_CHAT_MODE.bat'.
echo ============================================================
pause
