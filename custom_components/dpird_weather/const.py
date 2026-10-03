"""Constants for the DPIRD Weather integration."""

from datetime import timedelta
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "dpird_weather"
ATTRIBUTION = (
    "Data provided by the Western Australian Department of Primary Industries "
    "and Regional Development (DPIRD)"
)

CONF_STATION = "station_code"
CONF_STATION_NAME = "station_name"

API_BASE = "https://api.agric.wa.gov.au/v2/weather/stations"
TIMEZONE = "Australia/Perth"
UPDATE_INTERVAL = timedelta(minutes=5)
