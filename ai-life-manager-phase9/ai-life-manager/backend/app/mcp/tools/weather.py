"""MCP weather tools — Open-Meteo, no API key required."""

from app.mcp.logging import log_tool_execution
from app.mcp.server import mcp
from app.services.weather_service import WeatherService


@mcp.tool
@log_tool_execution("get_current_weather")
async def get_current_weather(location: str, user_id: int | None = None) -> dict:
    """
    Current weather conditions for a location (city name, e.g.
    'Bengaluru' or 'London, UK'). Includes temperature, humidity, wind,
    precipitation, and a plain-language description. `rain_expected` is
    true if precipitation is currently being recorded.
    """
    service = WeatherService()
    result = await service.get_current_weather(location=location)
    return {"success": True, "weather": result}


@mcp.tool
@log_tool_execution("get_forecast")
async def get_forecast(location: str, days: int = 3, user_id: int | None = None) -> dict:
    """
    Daily weather forecast for a location, 1-16 days ahead (default 3).
    Each day includes high/low temperature, precipitation, chance of
    rain, and a plain-language description - useful for answering
    'will it rain tomorrow' or 'do I need an umbrella this week'.
    """
    service = WeatherService()
    result = await service.get_forecast(location=location, days=days)
    return {"success": True, **result}
