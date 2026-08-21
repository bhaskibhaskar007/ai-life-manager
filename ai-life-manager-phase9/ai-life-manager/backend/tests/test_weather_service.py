"""
Tests for WeatherService, using a fake httpx.AsyncClient that returns
canned in-process Response objects shaped like real Open-Meteo
responses — no real network call, and safe to run in any environment
(including this offline sandbox and CI).
"""

import httpx
import pytest

from app.services.weather_service import WeatherService, describe_weather_code


class FakeAsyncClient:
    """Minimal stand-in for httpx.AsyncClient: routes .get() calls to canned responses by URL."""

    def __init__(self, responses: dict[str, dict]):
        # responses: {url_substring: json_payload}
        self._responses = responses

    async def get(self, url: str, params: dict | None = None) -> httpx.Response:
        for substring, payload in self._responses.items():
            if substring in url:
                return httpx.Response(200, json=payload, request=httpx.Request("GET", url))
        raise AssertionError(f"No fake response configured for URL: {url}")

    async def aclose(self) -> None:
        pass


GEOCODE_RESPONSE = {
    "results": [{"name": "Bengaluru", "country": "India", "latitude": 12.9716, "longitude": 77.5946}]
}

CURRENT_WEATHER_RESPONSE = {
    "current": {
        "time": "2026-08-09T12:00",
        "temperature_2m": 27.4,
        "precipitation": 0.0,
        "weather_code": 2,
        "wind_speed_10m": 11.3,
        "relative_humidity_2m": 65,
    }
}

FORECAST_RESPONSE = {
    "daily": {
        "time": ["2026-08-10", "2026-08-11", "2026-08-12"],
        "temperature_2m_max": [29.1, 28.5, 27.9],
        "temperature_2m_min": [21.0, 20.8, 20.5],
        "precipitation_sum": [0.0, 5.2, 0.0],
        "precipitation_probability_max": [10, 65, 20],
        "weather_code": [1, 63, 2],
    }
}


@pytest.mark.asyncio
async def test_describe_weather_code_known():
    assert describe_weather_code(0) == "Clear sky"
    assert describe_weather_code(95) == "Thunderstorm"


@pytest.mark.asyncio
async def test_describe_weather_code_unknown():
    assert "Unknown" in describe_weather_code(9999)


@pytest.mark.asyncio
async def test_get_current_weather_parses_response():
    fake_client = FakeAsyncClient(
        {"geocoding-api.open-meteo.com": GEOCODE_RESPONSE, "api.open-meteo.com": CURRENT_WEATHER_RESPONSE}
    )
    service = WeatherService(http_client=fake_client)
    result = await service.get_current_weather(location="Bengaluru")

    assert result["location"] == "Bengaluru"
    assert result["temperature_celsius"] == 27.4
    assert result["conditions"] == "Partly cloudy"
    assert result["rain_expected"] is False


@pytest.mark.asyncio
async def test_get_current_weather_location_not_found():
    fake_client = FakeAsyncClient({"geocoding-api.open-meteo.com": {"results": []}})
    service = WeatherService(http_client=fake_client)

    with pytest.raises(ValueError, match="Could not find a location"):
        await service.get_current_weather(location="Nowhereville")


@pytest.mark.asyncio
async def test_get_forecast_parses_multiple_days():
    fake_client = FakeAsyncClient(
        {"geocoding-api.open-meteo.com": GEOCODE_RESPONSE, "api.open-meteo.com": FORECAST_RESPONSE}
    )
    service = WeatherService(http_client=fake_client)
    result = await service.get_forecast(location="Bengaluru", days=3)

    assert len(result["forecast"]) == 3
    # Day 2 has 65% rain probability (>=40 threshold) — should be flagged.
    assert result["forecast"][1]["rain_expected"] is True
    assert result["forecast"][1]["conditions"] == "Moderate rain"
    # Day 1 has 10% probability — should not be flagged.
    assert result["forecast"][0]["rain_expected"] is False


@pytest.mark.asyncio
async def test_get_forecast_rejects_out_of_range_days():
    service = WeatherService(http_client=FakeAsyncClient({}))
    with pytest.raises(ValueError, match="between 1 and 16"):
        await service.get_forecast(location="Bengaluru", days=30)
