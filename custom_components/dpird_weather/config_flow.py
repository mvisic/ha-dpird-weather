"""Config flow for DPIRD Weather."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import (
    DPIRDApiClient,
    DPIRDApiClientAuthenticationError,
    DPIRDApiClientCommunicationError,
    DPIRDApiClientError,
)
from .const import CONF_STATION, CONF_STATION_NAME, DOMAIN, LOGGER

API_KEY_URL = "https://weather.agric.wa.gov.au/developer-api"

class DPIRDConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ask for an API key, then let the user pick a weather station."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise the flow."""
        self._api_key: str = ""
        self._stations: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 1: API key. It's validated by downloading the station list."""
        errors: dict[str, str] = {}
        if user_input is not None:
            client = DPIRDApiClient(
                user_input[CONF_API_KEY].strip(), async_get_clientsession(self.hass)
            )
            try:
                stations = await client.async_get_stations()
            except DPIRDApiClientAuthenticationError:
                errors["base"] = "auth"
            except DPIRDApiClientCommunicationError:
                errors["base"] = "connection"
            except DPIRDApiClientError as exception:
                LOGGER.exception(exception)
                errors["base"] = "unknown"
            else:
                self._stations = {
                    s["stationCode"]: s.get("stationName", s["stationCode"])
                    for s in stations
                    if s.get("stationCode")
                }
                if self._stations:
                    self._api_key = user_input[CONF_API_KEY].strip()
                    return await self.async_step_station()
                errors["base"] = "no_stations"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    )
                }
            ),
            errors=errors,
        )

    async def async_step_station(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 2: choose the weather station."""
        if user_input is not None:
            code = user_input[CONF_STATION]
            await self.async_set_unique_id(code)
            self._abort_if_unique_id_configured()
            name = self._stations[code]
            return self.async_create_entry(
                title=name,
                data={
                    CONF_API_KEY: self._api_key,
                    CONF_STATION: code,
                    CONF_STATION_NAME: name,
                },
            )

        options = [
            SelectOptionDict(value=code, label=f"{name} ({code})")
            for code, name in sorted(self._stations.items(), key=lambda i: i[1])
        ]
        return self.async_show_form(
            step_id="station",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STATION): SelectSelector(
                        SelectSelectorConfig(
                            options=options,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
        )
