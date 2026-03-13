@echo off
echo PRE-START HEALTH CHECK: Synchronizing Brain...
.\ai-service\venv\Scripts\python.exe sync_brain.py

start "1. Frontend (UI) on :3000" cmd /k "cd frontend && npm start"
start "2. Backend (API) on :5001" cmd /k "cd backend && node server.js"
start "3. AI Admin Server on :8000" cmd /k "cd ai-service && .\venv\Scripts\activate && python admin_server.py"
start "4. Rasa Action Server on :5055" cmd /k "cd ai-service && .\venv\Scripts\activate && rasa run actions"
start "5. Rasa NLU Server on :5005" cmd /k "cd ai-service && .\venv\Scripts\activate && rasa run --enable-api --cors *"
echo All servers launched.
