"""
AI Life Manager — FastAPI application entrypoint.

Wires up the app shell (CORS, health check, exception handlers), mounts the
FastMCP server under /mcp, and registers all authenticated REST endpoints under /api/v1.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    analytics as analytics_routes,
    auth as auth_routes,
    budgets as budget_routes,
    chat as chat_routes,
    expenses as expense_routes,
    planner as planner_routes,
    preferences as preference_routes,
    reminders as reminder_routes,
)
from app.config import get_settings
from app.mcp.server import create_mcp_app

settings = get_settings()

# Build the MCP ASGI app first — its lifespan is passed to FastAPI
mcp_app = create_mcp_app()

app = FastAPI(
    title=settings.app_name,
    description="A context-aware personal AI assistant powered by FastMCP.",
    version="1.0.0",
    lifespan=mcp_app.lifespan,
)

# Mount FastMCP server under /mcp for MCP protocol communication
app.mount("/mcp", mcp_app)

# Configure CORS for frontend SPA access
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
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env, "version": "1.0.0"}


# Register all REST routers under api_v1_prefix (/api/v1)
app.include_router(auth_routes.router, prefix=settings.api_v1_prefix)
app.include_router(expense_routes.router, prefix=settings.api_v1_prefix)
app.include_router(reminder_routes.router, prefix=settings.api_v1_prefix)
app.include_router(budget_routes.router, prefix=settings.api_v1_prefix)
app.include_router(analytics_routes.router, prefix=settings.api_v1_prefix)
app.include_router(preference_routes.router, prefix=settings.api_v1_prefix)
app.include_router(planner_routes.router, prefix=settings.api_v1_prefix)
app.include_router(chat_routes.router, prefix=settings.api_v1_prefix)
