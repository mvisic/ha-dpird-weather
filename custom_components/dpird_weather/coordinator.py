"""DataUpdateCoordinator for DPIRD Weather."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    DPIRDApiClient,
    DPIRDApiClientAuthenticationError,
    DPIRDApiClientError,
)
from .const import CONF_STATION, DOMAIN, LOGGER, UPDATE_INTERVAL

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

type DPIRDConfigEntry = ConfigEntry[DPIRDCoordinator]


class DPIRDCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Fetch latest observations and the daily summary for one station."""

    config_entry: DPIRDConfigEntry

    def __init__(self, hass: HomeAssistant, entry: DPIRDConfigEntry) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{entry.data[CONF_STATION]}",
            update_interval=UPDATE_INTERVAL,
        )
        self.station_code: str = entry.data[CONF_STATION]
        self.client = DPIRDApiClient(
            entry.data["api_key"], async_get_clientsession(hass)
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch data from the API."""
        # Imported here to avoid a circular import with sensor.py
        from .sensor import DAILY_KEYS, LATEST_KEYS  # noqa: PLC0415

        try:
            latest = await self.client.async_get_latest(self.station_code, LATEST_KEYS)
        except DPIRDApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except DPIRDApiClientError as exception:
            raise UpdateFailed(exception) from exception

        # The daily summary is a bonus - don't fail the update if it's missing.
        try:
            daily = await self.client.async_get_daily(self.station_code, DAILY_KEYS)
        except DPIRDApiClientError as exception:
            LOGGER.debug("Daily summary unavailable: %s", exception)
            daily = {}

        LOGGER.debug("Latest keys: %s", sorted(latest))
        LOGGER.debug("Daily keys: %s", sorted(daily))
        return {"latest": latest, "daily": daily}
