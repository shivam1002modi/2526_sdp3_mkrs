# MBS — MKRS Benchmark System Index

This folder contains all official benchmark runs for the MKRS AI Brain.

## How to Run a New Test

```powershell
# From the project root (optionally pass a test name):
.\ai-service\venv\Scripts\python.exe ai-service\eval_v1.py
.\ai-service\venv\Scripts\python.exe ai-service\eval_v1.py --name "After Phi-3 Upgrade"
```

---

## Test History

| Test | TMS Score | Date | What Changed |
| :--- | :---: | :--- | :--- |
| [TEST_01_BASELINE](./TEST_01_BASELINE/REPORT.md) | **68.2** | 2026-02-21 | BASELINE |

---

## Scoring Reference

| TMS Range | Grade |
| :--- | :--- |
| 89 - 100 | EXCELLENT |
| 76 - 88 | GOOD |
| 61 - 75 | MODERATE |
| 41 - 60 | WEAK |
| 0 - 40 | CRITICAL |

See [PROCEDURE.md](./PROCEDURE.md) for full scoring rules.
