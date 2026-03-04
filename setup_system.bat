@echo off
setlocal

echo ============================================================
echo   MKRS - Language Agnostic Chatbot : One-Click Setup
echo ============================================================
echo.

:: --- Check for Python ---
echo [1/4] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8-3.11 and add to PATH.
    pause
    exit /b 1
)

:: --- Setup AI Service (Python) ---
echo [2/4] Setting up AI Service (Python Virtual Environment)...
cd ai-service
if not exist venv (
    python -m venv venv
    echo Virtual environment created.
)
call .\venv\Scripts\activate
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b 1
)
cd ..

:: --- Setup Backend (Node.js) ---
echo [3/4] Installing Backend dependencies...
cd backend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Backend dependencies.
    pause
    exit /b 1
)
cd ..

:: --- Setup Frontend (Node.js) ---
echo [4/4] Installing Frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Frontend dependencies.
    pause
    exit /b 1
)
cd ..

:: --- Final Checks ---
echo.
echo ============================================================
echo   SETUP COMPLETED SUCCESSFULLY!
echo ============================================================
echo.
echo IMPORTANT:
echo 1. Ensure Ollama is installed and running (https://ollama.com/)
echo 2. Run 'ollama pull llama3' before starting
echo 3. Run 'start_system.bat' to launch all microservices
echo.
pause
