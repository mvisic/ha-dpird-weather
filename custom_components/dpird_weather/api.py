"""API client for the DPIRD Weather 2.0 API."""

from __future__ import annotations

import asyncio
import socket
from datetime import datetime
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

import aiohttp

from .const import API_BASE, TIMEZONE

if TYPE_CHECKING:
    from collections.abc import Iterable

PAGE_SIZE = 200
HTTP_UNAUTHORISED = 401
HTTP_FORBIDDEN = 403
HTTP_TOO_MANY_REQUESTS = 429


class DPIRDApiClientError(Exception):
    """Base exception for the DPIRD API client."""


class DPIRDApiClientCommunicationError(DPIRDApiClientError):
    """Raised when the API can't be reached."""


class DPIRDApiClientAuthenticationError(DPIRDApiClientError):
    """Raised when the API key is rejected."""


class DPIRDApiClientRateLimitError(DPIRDApiClientError):
    """Raised when the API rate limit is hit."""


def _records(payload: Any) -> list[dict[str, Any]]:
    """Pull the list of records out of an API response."""
    if not isinstance(payload, dict):
        return []
    records = payload.get("collection", payload.get("data", []))
    if isinstance(records, dict):
        return [records]
    return records if isinstance(records, list) else []


def _lowest_sensor(items: list[Any]) -> dict[str, Any] | None:
    """Pick the lowest-height sensor from a list (e.g. wind), else the first."""
    sensors = [i for i in items if isinstance(i, dict)]
    if not sensors:
        return None
    with_height = [i for i in sensors if isinstance(i.get("height"), (int, float))]
    return min(with_height, key=lambda i: i["height"]) if with_height else sensors[0]


def _flatten(record: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """
    Flatten nested records into camelCase keys.

    {"airTemperature": {"max": 20}} becomes {"airTemperatureMax": 20}.
    Sensor arrays such as wind use the lowest sensor, so
    {"wind": [{"height": 3, "avg": {"speed": 5}}]} becomes {"windAvgSpeed": 5}.
    """
    flat: dict[str, Any] = {}
    for key, value in record.items():
        name = f"{prefix}{key[:1].upper()}{key[1:]}" if prefix else key
        if isinstance(value, list):
            value = _lowest_sensor(value)  # noqa: PLW2901
        if isinstance(value, dict):
            flat.update(_flatten(value, name))
        elif value is not None or name not in flat:
            flat[name] = value
    return flat


def _first_summary(payload: Any) -> dict[str, Any]:
    """Return the first summary from a daily summary response."""
    if not isinstance(payload, dict):
        return {}
    container = payload.get("data")
    if container is None:
        collection = payload.get("collection")
        container = collection[0] if collection else {}
    summaries = container.get("summaries") if isinstance(container, dict) else None
    return summaries[0] if summaries else {}


class DPIRDApiClient:
    """Client for the DPIRD Weather 2.0 API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        """Initialise the client."""
        self._api_key = api_key
        self._session = session

    async def _get(self, path: str, params: dict[str, Any]) -> Any:
        """Make a GET request and return the decoded JSON."""
        headers = {"accept": "application/json", "API-KEY": self._api_key}
        try:
            async with asyncio.timeout(30):
                response = await self._session.get(
                    f"{API_BASE}{path}", headers=headers, params=params
                )
                if response.status in (HTTP_UNAUTHORISED, HTTP_FORBIDDEN):
                    msg = "Invalid DPIRD API key"
                    raise DPIRDApiClientAuthenticationError(msg)
                if response.status == HTTP_TOO_MANY_REQUESTS:
                    msg = "DPIRD API rate limit exceeded"
                    raise DPIRDApiClientRateLimitError(msg)
                response.raise_for_status()
                return await response.json()
        except TimeoutError as exception:
            msg = f"Timeout talking to the DPIRD API - {exception}"
            raise DPIRDApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error talking to the DPIRD API - {exception}"
            raise DPIRDApiClientCommunicationError(msg) from exception

    async def async_get_stations(self) -> list[dict[str, Any]]:
        """Return all open stations (code, name, location)."""
        stations: list[dict[str, Any]] = []
        offset = 0
        while True:
            payload = await self._get(
                "",
                {
                    "offset": offset,
                    "limit": PAGE_SIZE,
                    "includeClosed": "false",
                    "group": "api",
                    "select": "stationCode,stationName,latitude,longitude,status",
                },
            )
            page = _records(payload)
            stations.extend(page)
            if len(page) < PAGE_SIZE:
                return stations
            offset += PAGE_SIZE

    async def async_get_latest(
        self, station_code: str, keys: Iterable[str]
    ) -> dict[str, Any]:
        """Return the latest observations for a station."""
        payload = await self._get(
            f"/{station_code}/latest", {"select": ",".join(sorted(set(keys)))}
        )
        records = _records(payload)
        return _flatten(records[0]) if records else {}

    async def async_get_daily(
        self, station_code: str, keys: Iterable[str]
    ) -> dict[str, Any]:
        """Return today's daily summary for a station (Perth time)."""
        today = datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d")
        payload = await self._get(
            f"/{station_code}/summaries/daily",
            {
                "startDate": today,
                "endDate": today,
                "offset": 0,
                "limit": 1,
                "select": ",".join(sorted(set(keys))),
            },
        )
        summary = _first_summary(payload)
        return _flatten(summary) if summary else {}
