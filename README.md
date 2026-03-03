DocuBot: The Language Agnostic Chatbot 🤖📄

A locally-hosted, privacy-focused AI assistant that answers questions from your documents in multiple languages.

🎥 Watch the Demo Video  :https://youtu.be/v3KFLLyCE_g

🚀 Overview

DocuBot is a professional-grade Retrieval-Augmented Generation (RAG) system designed for educational institutions and organizations. It allows administrators to upload PDF documents (like exam timetables, policy documents, or educational material) and enables users to ask questions in natural language.

Key Differentiator: It runs entirely locally using open-source models. No data leaves your server, and no external API keys (like OpenAI or Google) are required, ensuring maximum privacy and zero recurring costs.

### 🧠 Context-Aware Ingestion (DeepDive V4)

Our RAG pipeline doesn't just "read" text; it understands the layout. This ensures high accuracy even for complex documents:

1.  **Layout Awareness**: Using Y-Axis and X-Axis Histograms, the system detects horizontal bands and columns. This prevents "column bleeding" where text from different columns is mixed together.
2.  **Artifact Removal**: Statistically analyzes headers and footers across the entire document to remove repetitive noisy artifacts.
3.  **Table Reconstruction**: Detects tables and converts them into structured Markdown format. These tables are treated as "atomic units" during ingestion.
4.  **Smart Chunking**: Unlike standard splitters that might break a table in half, our `SmartChunker` ensures that Markdown tables stay together in a single chunk, preserving the context and relationships between data cells.
5.  **Multilingual Support**: Automatically detects input language and maintains context across translations.

---

### ✨ Key Features

100% Local Intelligence: Powered by local Deep Learning models for retrieval, re-ranking, and text generation.

Advanced RAG Pipeline: Implements a sophisticated Retrieve -> Re-rank -> Generate architecture to ensure high-accuracy answers.

Multilingual Support: Automatically detects the user's language and translates answers (supports English, Hindi, Gujarati, etc.).

Admin Dashboard: Built-in interface to upload PDFs and trigger model retraining instantly with real-time log streaming.

Source Citations: Every answer links back to the specific source document and page number for verification.

Voice Interaction (Gemini-like): A fully hands-free conversational mode with real-time streaming transcription, auto-submit (silence detection), and anti-echo logic for a fluid voice-first experience.

🛠️ Tech Stack

Frontend

React.js: Modern, responsive user interface.

CSS: Custom styling with animations and responsive design.

Web Speech API: Native browser API used for low-latency Speech-to-Text (STT) and Text-to-Speech (TTS).

Backend

Node.js & Express: Serves as a secure proxy, handles file uploads, and serves static assets.

AI Service (The Brain)

Rasa Open Source: Handles conversation flow and NLU (Intent Recognition).

Python (FastAPI): Handles asynchronous admin tasks and model retraining.

LangChain & FAISS: Vector database management for efficient document retrieval.

Hugging Face & Ollama Models (Local):

Retrieval: ai4bharat/IndicBERT-v3-1B (Bi-Encoder)

Re-ranking: cross-encoder/ms-marco-MiniLM-L-6-v2 (Cross-Encoder)

Generation: mashriram/sarvam-1 (via Ollama)

🧠 System Architecture

The system follows a microservices architecture, ensuring modularity and scalability.

graph TD
    User[User (Browser)] <-->|React UI| Frontend
    Frontend <-->|REST API| Backend[Node.js Proxy]
    Backend <-->|Admin API| AdminServer[Admin Server (Python/FastAPI)]
    Backend <-->|Conversational API| RasaNLU[Rasa NLU Server]
    RasaNLU <-->|Action Request| RasaActions[Action Server (RAG Pipeline)]
    RasaActions <-->|Similarity Search| VectorDB[(FAISS Vector Store)]
    RasaActions <-->|Local Inference| LocalModels[Hugging Face Models]


### 🛠️ One-Click Setup & Run (Recommended)

To make it easier for new users, we've included automation scripts for the entire system:

1.  **Clone & Initial Setup**:
    ```powershell
    git clone https://github.com/shivam1002modi/language-agnostic-chatbot.git
    cd language-agnostic-chatbot
    ```

2.  **Run One-Click Installation**:
    Run the following command from the root directory. This will automatically create the Python virtual environment, install all Python dependencies (`requirements.txt`), and install all Node.js dependencies (`npm install`) for both the frontend and backend.
    ```powershell
    .\setup_system.bat
    ```

3.  **One-Click Launch**:
    Once setup is finished, pull the LLM and start all services:
    ```powershell
    # Pull the LLM (Requires Ollama running)
    ollama pull mashriram/sarvam-1

    # Launch all 5 microservices automatically
    .\start_system.bat
    ```

---

### 💻 Manual Run (Step-by-Step)

This system uses a microservices architecture. If you prefer manual control, follow these steps:

#### Prerequisites
*   **Node.js & npm**: For Frontend and Backend Proxy.
*   **Python 3.8 - 3.10**: Required for Rasa and AI Service.
*   **Virtual Environment**: Strongly recommended to avoid dependency conflicts.

#### 1. Setup AI Environment
Open a terminal in the `ai-service` folder.
```powershell
cd ai-service
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Start the Servers
Run each in a separate terminal OR use `start_system.bat`.

*   **Terminal 1: Frontend (UI)**: `cd frontend && npm install && npm start` (Port 3000)
*   **Terminal 2: Backend (Proxy)**: `cd backend && npm install && node server.js` (Port 5001)
*   **Terminal 3: AI Admin Server**: `cd ai-service && python admin_server.py` (Port 8000)
*   **Terminal 4: Rasa Actions**: `cd ai-service && rasa run actions` (Port 5055)
*   **Terminal 5: Rasa NLU**: `cd ai-service && rasa run --enable-api --cors "*"` (Port 5005)

---

### 📦 Key Dependencies
*   **Python**: `langchain`, `rasa`, `transformers`, `torch`, `faiss-cpu`, `chromadb`.
*   **Node.js**: `express`, `mongoose`, `multer`, `axios`, `react`.
*   **Models**: The system downloads models from Hugging Face on first run (Multi-lingual Bi-Encoder, Cross-Encoder, and BART-CNN).

---

📊 **MKRS Benchmark System (MBS)**

We've included a comprehensive benchmarking suite to measure the "Brain" quality across multiple dimensions.

**To Run a Benchmark:**
```powershell
cd ai-service
.\venv\Scripts\python.exe eval_v1.py
```
*   **Metrics measured**: Retrieval Hit Rate (RHR), Fact Accuracy (SEC), Hallucination Detection (NEG), Latency, and Memory usage.
*   **Output**: Automatically generates reports in `MBS/TEST_XX/REPORT.md`.

🧪 Testing Notes (`Shivam_test_zone`)

A dedicated test environment exists in `Shivam_test_zone` to verify voice components in isolation:
*   `TestSTT.html`: Tests real-time transcription and silence detection.
*   `TestTTS.html`: Tests voice selection (English/Hindi) and playback.
*   `TestCombined.html`: Verifies the complete hands-free loop (Anti-Echo & Auto-Resume).

Open these files directly in a browser to debug voice logic without running the full backend.
