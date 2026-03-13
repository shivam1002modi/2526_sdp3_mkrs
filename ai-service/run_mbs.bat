@echo off
setlocal

echo ============================================================
echo   MKRS Benchmark Runner (Automatic Testing)
echo ============================================================
echo.
echo [1/3] CLEANING UP SYSTEM RESOURCES...
echo This ensures no background Rasa processes consume RAM during the test.

:: Kill Rasa processes to free up RAM
taskkill /F /IM "rasa.exe" >nul 2>&1
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq 4. Rasa Action Server on :5055" >nul 2>&1
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq 5. Rasa NLU Server on :5005" >nul 2>&1

echo ✅ Background servers cleared.
echo.

echo [2/3] STARTING BENCHMARK (MBS)...
cd %~dp0
.\venv\Scripts\python.exe eval_v1.py --name "Optimized Brain Run"

echo.
echo [3/3] BENCHMARK COMPLETE.
echo.
echo To return to manual chat mode, run 'start_system.bat' from the root.
echo.
pause
