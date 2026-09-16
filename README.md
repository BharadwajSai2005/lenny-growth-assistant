# 🎙️ The Lenny Growth Assistant

A full-stack, AI-powered RAG chat assistant that ingests Lenny's Podcast transcripts to answer product & growth questions, generate Ship 30 for 30 essays, and render Markdown/HTML artifacts — all powered by a local LLM (Ollama).

## Architecture Overview

```mermaid
graph TD
    User <-->|HTTP| Frontend["React/Vite Frontend :5173"]
    Frontend <-->|REST API| Backend["FastAPI Backend :8000"]
    Backend <-->|pgvector| DB[("PostgreSQL + pgvector :5432")]
    Backend <-->|API| Ollama["Ollama tinyllama (Local)"]
    Backend <-.->|API| Anthropic["Anthropic Claude (Cloud, optional)"]
```

## Security & Untrusted Artifact Sandboxing

- The React Artifact Viewer uses a strict **defense-in-depth approach** to safely render AI-generated HTML content.
- Generated code is injected into an isolated `<iframe sandbox="allow-scripts">` environment.
- By deliberately omitting `allow-same-origin`, the artifact is completely blocked from accessing the parent application's cookies, local storage, or session state.
- **Why this matters:** It prevents Zero-Day XSS vulnerabilities from AI-hallucinated or maliciously prompted scripts.

## Testing Strategy (Automated & Manual)

- **Automated Tests:** Comprehensive `pytest` suite located in `backend/tests/`. It covers critical API endpoints, session persistence, and the core RAG/Skill routing logic (verifying precise switching between `qa` and `ship30` modes).
- **Manual Test Plan:** A rigorous 12-step UI/UX manual test plan is documented in `docs/manual_test_plan.md` to guarantee flawless frontend behavior, state management, RAG citations, and markdown rendering.

## Graceful Fallbacks & Resilience

- **Dual-LLM Support:** The backend automatically switches between Local (Ollama) and Cloud (Anthropic) providers via a simple `.env` toggle.
- **Dynamic UI:** The React frontend dynamically reflects the active model (e.g., `🖥️ tinyllama` vs `☁️ claude`) and degrades gracefully if a provider goes offline.
- **Resilient Ingestion:** The DB ingestion pipeline uses a bundled dataset but includes a GitHub API fallback if external dependencies fail.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Latest | PostgreSQL database |
| [Python](https://www.python.org/downloads/) | 3.10+ | Backend API |
| [Node.js](https://nodejs.org/) | 18+ | Frontend |
| [Ollama](https://ollama.com/download) | Latest | Local LLM inference |

---

## 🚀 Quick Start (Evaluator Setup)

### Step 1: Clone and configure
```bash
git clone <repo-url>
cd lenny-growth-assistant
cp .env.example .env
```

### Step 2: Start Ollama (local LLM)
```bash
# Pull the model (~637 MB download)
ollama pull tinyllama

# Start Ollama (keep this terminal open)
# On machines with limited GPU, force CPU mode:
# Windows CMD:
set CUDA_VISIBLE_DEVICES=
set OLLAMA_NUM_GPU=0
ollama serve

# Linux/Mac:
# CUDA_VISIBLE_DEVICES= OLLAMA_NUM_GPU=0 ollama serve
```
Verify: open http://localhost:11434 — should show "Ollama is running"

### Step 3: Start the database
```bash
docker compose up -d db
```
Verify: `docker ps` should show the pgvector container running on port 5432

### Step 4: Start the backend
```bash
cd backend
python -m venv venv

# Activate venv:
# Windows CMD: venv\Scripts\activate
# Windows PowerShell: venv\Scripts\Activate.ps1
# Linux/Mac: source venv/bin/activate

pip install -r requirements.txt

# Ingest transcript data into the database (one-time)
# If you encounter memory errors, set these first:
# Windows CMD: set OPENBLAS_NUM_THREADS=1 && set OMP_NUM_THREADS=1
# Linux/Mac: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python ingest.py

# Start the API server
uvicorn main:app --reload
```
Verify: open http://localhost:8000/health — should return `{"status":"ok","llm_provider":"local","database":"connected"}`

### Step 5: Start the frontend
Open a **new terminal**:
```bash
cd frontend
npm install
npm run dev
```

### Step 6: Use the app
Open **http://localhost:5173** in your browser.

Try these queries:
- `What is product-market fit?` — grounded Q&A with source citations
- `How do I improve retention?` — follow-up in same session
- `Write a Ship 30 for 30 essay about growth metrics` — generates essay in artifact viewer
- Click **+ New Chat** — fresh session

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `postgresql://postgres:postgres@localhost:5432/lenny` | PostgreSQL connection string |
| `LLM_PROVIDER` | Yes | `local` | `local` (Ollama) or `cloud` (Anthropic) |
| `OLLAMA_BASE_URL` | For local | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | For local | `tinyllama` | Ollama model name |
| `ANTHROPIC_API_KEY` | For cloud | — | Anthropic API key (only if `LLM_PROVIDER=cloud`) |

### Switching to Cloud LLM (Anthropic Claude)
```bash
# In .env:
LLM_PROVIDER=cloud
ANTHROPIC_API_KEY=sk-ant-your-key-here
```
Restart the backend — the UI badge will update to show ☁️ Claude.

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

Tests cover: API endpoints (health, config, chat, sessions), skill routing (Q&A vs Ship 30), and error handling.

See also: [`docs/manual_test_plan.md`](docs/manual_test_plan.md) for 12 manual UI test cases.

---

## API Endpoints

| Method | Path | Description | Request Body |
|--------|------|-------------|-------------|
| `GET` | `/health` | Health check + DB/LLM status | — |
| `GET` | `/config` | Current LLM provider and model | — |
| `POST` | `/chat` | Send a chat message | `{"message": "...", "session_id": "..."}` |
| `POST` | `/sessions` | Create a new chat session | — |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Database connection error** | Ensure Docker is running: `docker compose up -d db` |
| **Ollama connection refused** | Ensure Ollama is running: `ollama serve` |
| **CUDA out of memory** | Force CPU: `set CUDA_VISIBLE_DEVICES=` then restart `ollama serve` |
| **Memory error during ingest** | Set `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` before running `python ingest.py` |
| **Missing Anthropic key** | Only needed if `LLM_PROVIDER=cloud`. Set `ANTHROPIC_API_KEY` in `.env` |
| **Frontend build error** | Run `npm install` in the `frontend/` directory |

---

## Project Structure

```
lenny-growth-assistant/
├── backend/
│   ├── agent.py           # LLM agent with skill routing (QA + Ship30)
│   ├── database.py        # SQLAlchemy models + pgvector
│   ├── ingest.py          # Transcript ingestion (bundled + GitHub fallback)
│   ├── main.py            # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Backend container
│   └── tests/             # Automated tests
│       ├── test_api.py    # API endpoint tests
│       └── test_agent.py  # Skill routing tests
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # Main chat UI
│   │   ├── components/
│   │   │   └── ArtifactViewer.jsx     # Sandboxed artifact renderer
│   │   └── index.css                  # Dark theme styles
│   ├── Dockerfile         # Frontend container
│   └── package.json
├── docs/
│   ├── PRD.md             # Product requirements + architectural decisions
│   ├── architecture.md    # System architecture + DB schema + security
│   ├── design.md          # UI/UX principles + accessibility
│   └── manual_test_plan.md
├── agent-transcripts/     # AI-assisted development logs
├── .env.example           # Environment template (safe defaults)
├── .gitignore
├── docker-compose.yml     # Full stack: DB + backend + frontend
└── README.md              # This file
```

## Documentation

- [**PRD**](docs/PRD.md) — User, problem, success metrics, assumptions, scope, risks, architectural decisions
- [**Architecture**](docs/architecture.md) — DB schema, API endpoints, ingestion flow, security model
- [**Design**](docs/design.md) — UI principles, interaction states, responsive behavior, accessibility
- [**Manual Test Plan**](docs/manual_test_plan.md) — 12 manual test cases for UI verification
- [**Agent Transcripts**](agent-transcripts/README.md) — Development iterations, failed attempts, corrections
