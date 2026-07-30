"""API client for DPIRD Weather."""
from datetime import datetime
import aiohttp
from .const import API_DAILY, API_LATEST

class DPIRDApiClient:
    """Client to handle DPIRD requests."""

    def __init__(self, api_key: str, station_code: str, session: aiohttp.ClientSession) -> None:
        self._api_key = api_key
        self._station_code = station_code
        self._session = session

    async def async_get_data(self) -> dict:
        """Fetch latest weather and daily summaries concurrently."""
        headers = {"accept": "application/json", "API-KEY": self._api_key}
        today = datetime.now().strftime("%Y-%m-%d")

        latest_url = API_LATEST.format(station=self._station_code)
        daily_url = API_DAILY.format(station=self._station_code, date=today)

        async with aiohttp.ClientSession() as session:
            async with session.get(latest_url, headers=headers) as latest_resp:
                latest_data = await latest_resp.json() if latest_resp.status == 200 else {}

            async with session.get(daily_url, headers=headers) as daily_resp:
                daily_data = await daily_resp.json() if daily_resp.status == 200 else {}

        return {
            "latest": latest_data.get("data", {}),
            "daily": daily_data.get("data", [{}])[0] if daily_data.get("data") else {},
        }
