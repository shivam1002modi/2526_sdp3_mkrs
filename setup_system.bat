@echo off
setlocal

echo ============================================================
echo   MKRS - Language Agnostic Chatbot : One-Click Setup
echo ============================================================
echo.

:: --- Check for Python ---
echo [1/5] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8-3.11 and add to PATH.
    pause
    exit /b 1
)

:: --- Setup AI Service (Python) ---
echo [2/5] Setting up AI Service (Python Virtual Environment)...
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
echo [3/5] Installing Backend dependencies...
cd backend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Backend dependencies.
    pause
    exit /b 1
)
cd ..

:: --- Setup Frontend (Node.js) ---
echo [4/5] Installing Frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Frontend dependencies.
    pause
    exit /b 1
)
cd ..

:: --- Ollama Model Pull ---
echo [5/5] Ensuring Ollama model is available...
echo Attempting to pull llama3.2:3b (Balanced Config - Test 62)...
ollama pull llama3.2:3b
if %errorlevel% neq 0 (
    echo [WARNING] Could not pull model automatically. 
    echo Please ensure Ollama is running and manually run 'ollama pull llama3.2:3b'
)

:: --- Final Checks ---
echo.
echo ============================================================
echo   SETUP COMPLETED SUCCESSFULLY!
echo   Target Config: Test 62 Balanced (k=50, 3B Model)
echo ============================================================
echo.
echo IMPORTANT:
echo 1. Ensure Ollama is installed and running (https://ollama.com/)
echo 2. Verified model: llama3.2:3b [GOLDEN]
echo 3. Run 'start_system.bat' to launch all microservices
echo.
pause
