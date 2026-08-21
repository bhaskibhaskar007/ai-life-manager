"""
AI Life Manager — FastAPI application entrypoint.

This file only wires up the app shell (CORS, health check, router
mounting). Actual REST routes, the MCP server, and startup/shutdown
hooks for DB + MCP client connections are added in later phases.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="A context-aware personal AI assistant powered by FastMCP.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health_check() -> dict:
    """Basic liveness check used by hosting platforms and Docker healthchecks."""
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


# NOTE: API routers (app.api.routes.*) and the MCP server mount
# (app.mcp.server) are registered here starting in Phase 3/4.
