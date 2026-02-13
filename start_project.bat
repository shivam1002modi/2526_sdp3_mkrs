@echo off
ECHO --- 2526_sdp3_mkrs Project Launcher ---
ECHO.

ECHO [1/3] Starting Backend Server...
cd backend
start "Backend Server" cmd /k "echo Starting Backend... & npm start"
cd ..

ECHO [2/3] Starting Frontend Application...
cd frontend
start "Frontend App" cmd /k "echo Starting Frontend... & npm start"
cd ..

ECHO [3/3] Starting AI Service (Rasa & RAG)...
REM Run retrain.bat or just run rasa? 
REM retrain.bat runs rag_pipeline and rasa train.
REM We simply want to run the rasa server usually, but retrain.bat seems to be the main entry per the user repo structure.
REM But typically for a running systems we need 'rasa run'.
REM Looking at backend/routes/chatRoutes.js, it expects Rasa at http://localhost:5005/webhooks/rest/webhook
REM So we need to run 'rasa run --enable-api --cors "*"'

ECHO Starting Rasa Server...
cd ai-service
start "Rasa Server" cmd /k "..\.venv\Scripts\activate & echo Starting Rasa... & rasa run --enable-api --cors "*" --debug"
start "Admin Server" cmd /k "..\.venv\Scripts\activate & echo Starting Admin Server... & python admin_server.py"
cd ..

ECHO.
ECHO All services have been launched in separate windows.
ECHO Backend: http://localhost:5001
ECHO Frontend: http://localhost:3000
ECHO Rasa: http://localhost:5005
ECHO.
PAUSE
