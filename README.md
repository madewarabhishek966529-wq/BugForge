# BugForge

**AI-Powered Runtime Bug Detection and Debugging Platform**

BugForge is an intelligent debugging application designed for Python projects. It integrates static analysis (Ruff, Pylint, AST analysis), controlled local runtime execution via subprocesses, stack trace parsing, relevant context extraction, and AI-driven root-cause analysis with safe fix suggestions.

---

## 🛠 Project Architecture

- **Backend:** FastAPI (Python 3.12+)
- **Frontend:** Streamlit
- **Database:** PostgreSQL (with SQLite fallback for local development)
- **Static Analyzers:** Ruff, Pylint, Python AST
- **Runtime Runner:** Direct local Python subprocess execution with process timeouts and security context stripping

---

## 🚀 Quick Start Guide

### 1. Environment Setup

Create and activate a virtual environment:

```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

Install backend and frontend dependencies:

```powershell
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env`:

```powershell
cp .env.example .env
```

Set execution parameters in `.env`:
```text
RUNTIME_TIMEOUT=30
PYTHON_EXECUTABLE=python
```

### 3. Run FastAPI Backend

```powershell
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify backend health check at:
`http://127.0.0.1:8000/health`

### 4. Run Streamlit Frontend

In a separate terminal tab:

```powershell
streamlit run frontend/app.py
```

Open your browser at `http://localhost:8501`.

---

## 🔒 Security Notice for Runtime Execution

BugForge executes Python projects directly using local subprocesses.

- Only run projects that you trust.
- API keys and internal secrets are stripped from subprocess environments.
- Execution is constrained by `RUNTIME_TIMEOUT` (default: 30s).
- Subprocesses are terminated automatically if execution exceeds the timeout.

---

## 🧪 Running Tests

```powershell
python -m pytest backend/tests
```

---

## 📁 Repository Layout

```text
BugForge/
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI App Entrypoint
│   │   ├── api/                # REST API Endpoints (Projects, Bugs)
│   │   ├── core/               # Configuration & Security Settings
│   │   ├── database/           # DB Session & Table Initialization
│   │   ├── models/             # SQLAlchemy ORM Models
│   │   ├── schemas/            # Pydantic Schemas
│   │   ├── services/           # Business Logic Services
│   │   ├── analyzers/          # Static & Local Runtime Analyzers
│   │   └── ai/                 # AI Provider Abstraction
│   ├── tests/                  # Pytest suite
│   └── requirements.txt
├── frontend/
│   ├── app.py                  # Streamlit Multi-page App Main File
│   ├── pages/                  # Streamlit Dashboard & Navigation Pages
│   └── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```
