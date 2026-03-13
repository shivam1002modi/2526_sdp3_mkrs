# 🧠 MKRS AI Brain - Quick Start Guide

This guide describes how to run the MKRS system in its two primary modes. Both modes are **Plug & Play** and feature automatic hardware optimization.

---

## 🚀 1. Manual Chat Mode (User Interface)
Use this mode to interact with the AI through the web browser.

**Command:**
```powershell
.\LAUNCH_CHAT_MODE.bat
```

**What it does:**
*   **Clears RAM**: Instantly kills any background tests or stale processes.
*   **Optimizes CPU**: Pins Ollama to 8 threads and sets process priority to **HIGH**.
*   **Starts All Servers**: Launches the Frontend (:3000), Backend (:5001), and Rasa AI Engine (:5005).

---

## 📊 2. Automatic Testing Mode (Benchmark)
Use this mode to run the **MBS (MKRS Benchmark System)** and verify accuracy/latency.

**Command:**
```powershell
.\LAUNCH_BENCHMARK_MODE.bat
```

**What it does:**
*   **RAM Recovery**: Kills all chat windows to free up **10GB+ of RAM**.
*   **Runs MBS**: Executes a full 30-question diagnostic suit covering standard facts and stress tests.
*   **Archives Reports**: Saves a detailed analysis to the `MBS/` directory.

---

## ⚠️ Important Notes
*   **Self-Cleaning**: Running one mode will automatically shut down the other. This prevents memory crashes and ensures 100% accuracy.
*   **CPU Priority**: The system is tuned for high-performance inference on CPU. Ensure **Ollama** is running before starting.

---
*Last Updated: 2026-03-13*
