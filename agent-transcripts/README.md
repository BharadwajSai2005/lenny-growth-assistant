# Agent Transcripts

This folder contains logs from the AI-assisted development process of the Lenny Growth Assistant.

## Development Process

The project was built with AI coding assistance (Antigravity / Claude). Below is a summary of the development trajectory, including failed attempts and corrections.

## Key Development Iterations

### Iteration 1: Initial Scaffold
- Generated basic FastAPI + React + PostgreSQL scaffold
- Used `langchain` with `langchain-community` imports
- **Issue**: `langchain.schema` imports failed with newer langchain versions
- **Fix**: Migrated to `langchain_core.messages` imports

### Iteration 2: SQLAlchemy 2.x Compatibility
- Database initialization used raw SQL strings: `conn.execute("CREATE EXTENSION IF NOT EXISTS vector")`
- **Issue**: SQLAlchemy 2.x requires `text()` wrapper for raw SQL
- **Fix**: Wrapped in `text()` and added `conn.commit()`

### Iteration 3: Ollama Integration
- Initial import: `from langchain_community.chat_models import ChatOllama`
- **Issue**: `ChatOllama` moved to separate `langchain-ollama` package in newer versions
- **Fix**: Lazy import from `langchain_ollama` with graceful fallback if not installed

### Iteration 4: Data Source Unavailability
- Original ingestion script fetched from `ChatPRD/lennys-podcast-transcripts` GitHub repo
- **Issue**: GitHub API returned 404 — repo is unavailable
- **Fix**: Bundled 11 realistic transcript-style chunks directly in `ingest.py` with GitHub as fallback

### Iteration 5: Memory Constraints
- `sentence-transformers` + PyTorch caused `MemoryError` and `OpenBLAS` allocation failures on 16GB RAM machine
- **Fix**: Set `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` environment variables to limit parallel memory allocation

### Iteration 6: GPU Memory (CUDA OOM)
- Ollama `phi3_custom` model crashed with `cudaMalloc failed: out of memory` on 4GB GPU
- **Fix**: Force CPU-only inference with `CUDA_VISIBLE_DEVICES=` and `OLLAMA_NUM_GPU=0`, switched to smaller `tinyllama` model

### Iteration 7: Frontend Overhaul
- Original `App.css` was Vite boilerplate — not chat app styles
- `ArtifactViewer` used `sandbox=""` which blocked all rendering
- **Fix**: Complete CSS rewrite with dark theme, proper artifact viewer with `sandbox="allow-scripts"`, Preview/Code tabs, responsive design

### Iteration 8: Docker Build Issues
- Frontend Dockerfile used `nginx:slim` (non-existent tag)
- Alpine images caused `exec format error` on Windows/WSL2
- **Fix**: Used `node:20-slim` for build stage, `nginx:alpine` for serve stage

## Tools Used
- **Antigravity (Google)**: Primary AI coding assistant for code generation, debugging, and documentation
- **Ollama**: Local LLM inference
- **Docker Desktop**: Container orchestration

## Note
All API keys, secrets, and sensitive data have been removed from these logs.
