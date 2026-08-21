"""
Weather service — Open-Meteo (free, no API key required).

Two-step lookup, matching Open-Meteo's actual API shape: geocode a
place name to lat/lon via the Geocoding API, then fetch weather for
those coordinates via the Forecast API.

`http_client` is injectable so tests can supply a fake client that
returns canned `httpx.Response` objects built in-process — no real
network call needed to test the parsing/error-handling logic.
"""

import httpx

from app.config import get_settings

settings = get_settings()

# WMO Weather interpretation codes, as documented by Open-Meteo.
WMO_CODE_DESCRIPTIONS: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def describe_weather_code(code: int) -> str:
    return WMO_CODE_DESCRIPTIONS.get(code, f"Unknown conditions (code {code})")


class WeatherService:
    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self._injected_client = http_client

    async def _request_json(self, client: httpx.AsyncClient, url: str, params: dict) -> dict:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise ValueError("The weather service is currently unavailable. Please try again shortly.") from None

    async def geocode(self, client: httpx.AsyncClient, location: str) -> dict:
        data = await self._request_json(
            client,
            f"{settings.open_meteo_geocoding_url}/search",
            {"name": location, "count": 1, "language": "en", "format": "json"},
        )
        results = data.get("results")
        if not results:
            raise ValueError(f"Could not find a location matching '{location}'.")
        top = results[0]
        return {
            "name": top["name"],
            "country": top.get("country"),
            "latitude": top["latitude"],
            "longitude": top["longitude"],
        }

    async def get_current_weather(self, *, location: str) -> dict:
        client = self._injected_client or httpx.AsyncClient(timeout=10.0)
        should_close = self._injected_client is None
        try:
            place = await self.geocode(client, location)
            data = await self._request_json(
                client,
                f"{settings.open_meteo_base_url}/forecast",
                {
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "current": "temperature_2m,precipitation,weather_code,wind_speed_10m,relative_humidity_2m",
                    "timezone": "auto",
                },
            )
            current = data.get("current", {})
            code = current.get("weather_code")
            return {
                "location": place["name"],
                "country": place["country"],
                "temperature_celsius": current.get("temperature_2m"),
                "humidity_percent": current.get("relative_humidity_2m"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "precipitation_mm": current.get("precipitation"),
                "conditions": describe_weather_code(code) if code is not None else "Unknown",
                "rain_expected": bool(current.get("precipitation", 0) and current["precipitation"] > 0),
                "observed_at": current.get("time"),
            }
        finally:
            if should_close:
                await client.aclose()

    async def get_forecast(self, *, location: str, days: int = 3) -> dict:
        if days < 1 or days > 16:
            raise ValueError("days must be between 1 and 16 (Open-Meteo's supported forecast range).")

        client = self._injected_client or httpx.AsyncClient(timeout=10.0)
        should_close = self._injected_client is None
        try:
            place = await self.geocode(client, location)
            data = await self._request_json(
                client,
                f"{settings.open_meteo_base_url}/forecast",
                {
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code,precipitation_probability_max",
                    "timezone": "auto",
                    "forecast_days": days,
                },
            )
            daily = data.get("daily", {})
            dates = daily.get("time", [])
            forecast_days = []
            for i, day in enumerate(dates):
                code = daily.get("weather_code", [None] * len(dates))[i]
                precip_prob = daily.get("precipitation_probability_max", [None] * len(dates))[i]
                forecast_days.append(
                    {
                        "date": day,
                        "temp_max_celsius": daily.get("temperature_2m_max", [None] * len(dates))[i],
                        "temp_min_celsius": daily.get("temperature_2m_min", [None] * len(dates))[i],
                        "precipitation_mm": daily.get("precipitation_sum", [None] * len(dates))[i],
                        "chance_of_rain_percent": precip_prob,
                        "conditions": describe_weather_code(code) if code is not None else "Unknown",
                        "rain_expected": bool(precip_prob is not None and precip_prob >= 40),
                    }
                )
            return {"location": place["name"], "country": place["country"], "forecast": forecast_days}
        finally:
            if should_close:
                await client.aclose()
