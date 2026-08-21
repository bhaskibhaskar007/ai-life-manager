"""
Centralized application configuration.

All settings are loaded from environment variables (via a `.env` file in
development). Nothing sensitive is ever hardcoded here — this module only
defines *names, types, and defaults*.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "AI Life Manager"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./ai_life_manager.db"

    # --- Auth / JWT ---
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # --- CORS ---
    cors_allowed_origins: str = "http://localhost:5173"

    # --- LLM ---
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # --- Weather ---
    open_meteo_base_url: str = "https://api.open-meteo.com/v1"

    # --- MCP ---
    mcp_server_transport: str = "streamable-http"
    mcp_server_host: str = "127.0.0.1"
    mcp_server_port: int = 8001

    # --- Rate limiting ---
    rate_limit_default: str = "100/minute"
    rate_limit_auth: str = "10/minute"

    # --- Logging ---
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor. Import and call `get_settings()` anywhere
    that needs config — never instantiate `Settings()` directly outside
    this module, so we have exactly one source of truth per process.
    """
    return Settings()
