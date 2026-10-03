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
        return records[0] if records else {}

    async def async_get_daily(
        self, station_code: str, keys: Iterable[str]
    ) -> dict[str, Any]:
        """Return today's daily summary for a station (Perth time)."""
        today = datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d")
        payload = await self._get(
            "/summaries/daily",
            {
                "startDate": today,
                "endDate": today,
                "stationCode": station_code,
                "offset": 0,
                "limit": 25,
                "includeClosed": "false",
                "select": ",".join(sorted(set(keys))),
            },
        )
        records = _records(payload)
        return records[0] if records else {}
