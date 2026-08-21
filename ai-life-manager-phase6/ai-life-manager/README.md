# AI Life Manager

> A context-aware personal AI assistant powered by FastMCP — connecting an LLM to expense tracking, analytics, reminders, budgets, weather, and memory tools through the Model Context Protocol.

**Status:** 🚧 Under active development (Phase 1 of 18 complete — repository scaffold)

Full documentation (architecture, MCP tool reference, API docs, setup, deployment) will be built out progressively as each phase lands. See `docs/` for design notes in the meantime.

## Quickstart (development)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env with real secrets
uvicorn app.main:app --reload
```

Visit http://localhost:8000/health — you should see `{"status": "ok", ...}`.

## Project structure

```
ai-life-manager/
├── backend/        # FastAPI + FastMCP server
├── frontend/        # React + Vite dashboard
├── docs/             # Architecture & design docs
├── docker-compose.yml
└── README.md
```
