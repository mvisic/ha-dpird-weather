"""Sensor platform for DPIRD Weather."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfIrradiance,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_STATION_NAME, DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import DPIRDConfigEntry, DPIRDCoordinator

PARALLEL_UPDATES = 0

TEMP = UnitOfTemperature.CELSIUS
MM = UnitOfLength.MILLIMETERS
KMH = UnitOfSpeed.KILOMETERS_PER_HOUR
MEASUREMENT = SensorStateClass.MEASUREMENT

# Sensors enabled by default; everything else is available but disabled.
DEFAULT_ENABLED = {
    ("latest", "airTemperature"),
    ("latest", "apparentTemperature"),
    ("latest", "relativeHumidity"),
    ("latest", "dewPoint"),
    ("latest", "barometricPressure"),
    ("latest", "rainfallSince9AM"),
    ("latest", "windAvgSpeed"),
    ("latest", "windMaxSpeed"),
    ("latest", "solarIrradiance"),
    ("latest", "soilTemperature"),
    ("daily", "airTemperatureMax"),
    ("daily", "airTemperatureMin"),
    ("daily", "rainfall"),
}


@dataclass(frozen=True, kw_only=True)
class DPIRDSensorEntityDescription(SensorEntityDescription):
    """Describes a DPIRD sensor."""

    data_type: str  # "latest" or "daily"


def _d(  # noqa: PLR0913
    data_type: str,
    key: str,
    name: str,
    unit: str | None,
    device_class: SensorDeviceClass | None = None,
    state_class: SensorStateClass | None = MEASUREMENT,
) -> DPIRDSensorEntityDescription:
    prefix = "Daily " if data_type == "daily" else ""
    return DPIRDSensorEntityDescription(
        key=f"{data_type}_{key}",
        data_type=data_type,
        name=f"{prefix}{name}",
        native_unit_of_measurement=unit,
        device_class=device_class,
        state_class=state_class,
        entity_registry_enabled_default=(data_type, key) in DEFAULT_ENABLED,
    )


_T = SensorDeviceClass.TEMPERATURE
_P = SensorDeviceClass.PRECIPITATION
_H = SensorDeviceClass.HUMIDITY
_PR = SensorDeviceClass.PRESSURE
_W = SensorDeviceClass.WIND_SPEED
_V = SensorDeviceClass.VOLTAGE
_TOTAL = SensorStateClass.TOTAL
_INC = SensorStateClass.TOTAL_INCREASING
_VOLT = UnitOfElectricPotential.VOLT
_HPA = UnitOfPressure.HPA
_MJ = "MJ/m²"

SENSOR_DESCRIPTIONS: tuple[DPIRDSensorEntityDescription, ...] = (
    # --- Latest observations ---
    _d("latest", "airTemperature", "Air temperature", TEMP, _T),
    _d("latest", "airTemperatureMinLast24Hrs", "Air temperature min (24 h)", TEMP, _T),
    _d("latest", "airTemperatureMaxLast24Hrs", "Air temperature max (24 h)", TEMP, _T),
    _d("latest", "airTemperatureLow6PMto9AM", "Air temperature low 6PM-9AM", TEMP, _T),
    _d(
        "latest", "airTemperatureHigh6AMto9PM", "Air temperature high 6AM-9PM", TEMP, _T
    ),
    _d("latest", "apparentTemperature", "Apparent temperature", TEMP, _T),
    _d("latest", "barometricPressure", "Barometric pressure", _HPA, _PR),
    _d("latest", "batteryVoltage", "Battery voltage", _VOLT, _V),
    _d("latest", "deltaT", "Delta T", TEMP),
    _d("latest", "dewPoint", "Dew point", TEMP, _T),
    _d("latest", "etoShortCrop", "ETo short crop", MM),
    _d("latest", "etoTallCrop", "ETo tall crop", MM),
    _d("latest", "etoShortCropTo3PM", "ETo short crop to 3PM", MM),
    _d("latest", "etoTallCropTo3PM", "ETo tall crop to 3PM", MM),
    _d("latest", "panEvaporation", "Pan evaporation", MM),
    _d("latest", "panEvaporation12AM", "Pan evaporation since 12AM", MM),
    _d("latest", "panEvaporationTo3PM", "Pan evaporation to 3PM", MM),
    _d("latest", "rainfallSince9AM", "Rainfall since 9AM", MM, _P, _INC),
    _d("latest", "rainfallTo9AM", "Rainfall to 9AM", MM, _P, _TOTAL),
    _d("latest", "rainfallTo3PM", "Rainfall to 3PM", MM, _P, _TOTAL),
    _d("latest", "relativeHumidity", "Relative humidity", PERCENTAGE, _H),
    _d("latest", "soilTemperature", "Soil temperature", TEMP, _T),
    _d("latest", "solarExposure", "Solar exposure", _MJ),
    _d(
        "latest",
        "solarIrradiance",
        "Solar irradiance",
        UnitOfIrradiance.WATTS_PER_SQUARE_METER,
        SensorDeviceClass.IRRADIANCE,
    ),
    _d("latest", "wetBulb", "Wet bulb", TEMP, _T),
    _d("latest", "windAvgSpeed", "Wind average speed", KMH, _W),
    _d("latest", "windMaxSpeed", "Wind max speed", KMH, _W),
    # --- Daily summary ---
    _d("daily", "airTemperatureAvg", "air temperature average", TEMP, _T),
    _d("daily", "airTemperatureMax", "air temperature max", TEMP, _T),
    _d("daily", "airTemperatureMin", "air temperature min", TEMP, _T),
    _d("daily", "apparentAirTemperatureAvg", "apparent temperature average", TEMP, _T),
    _d("daily", "apparentAirTemperatureMax", "apparent temperature max", TEMP, _T),
    _d("daily", "apparentAirTemperatureMin", "apparent temperature min", TEMP, _T),
    _d("daily", "barometricPressureAvg", "barometric pressure average", _HPA, _PR),
    _d("daily", "barometricPressureMax", "barometric pressure max", _HPA, _PR),
    _d("daily", "barometricPressureMin", "barometric pressure min", _HPA, _PR),
    _d("daily", "batteryMinVoltage", "battery min voltage", _VOLT, _V),
    _d("daily", "chillHours", "chill hours", UnitOfTime.HOURS),
    _d("daily", "deltaTAvg", "Delta T average", TEMP),
    _d("daily", "deltaTMax", "Delta T max", TEMP),
    _d("daily", "deltaTMin", "Delta T min", TEMP),
    _d("daily", "dewPointAvg", "dew point average", TEMP, _T),
    _d("daily", "dewPointMax", "dew point max", TEMP, _T),
    _d("daily", "dewPointMin", "dew point min", TEMP, _T),
    _d("daily", "evapotranspiration", "evapotranspiration", MM),
    _d("daily", "evapotranspirationShortCrop", "ETo short crop", MM),
    _d("daily", "evapotranspirationTallCrop", "ETo tall crop", MM),
    _d("daily", "panEvaporation", "pan evaporation", MM),
    _d("daily", "rainfall", "rainfall total", MM, _P, _TOTAL),
    _d("daily", "relativeHumidityAvg", "relative humidity average", PERCENTAGE, _H),
    _d("daily", "relativeHumidityMax", "relative humidity max", PERCENTAGE, _H),
    _d("daily", "relativeHumidityMin", "relative humidity min", PERCENTAGE, _H),
    _d("daily", "soilTemperatureAvg", "soil temperature average", TEMP, _T),
    _d("daily", "soilTemperatureMax", "soil temperature max", TEMP, _T),
    _d("daily", "soilTemperatureMin", "soil temperature min", TEMP, _T),
    _d("daily", "solarExposure", "solar exposure", _MJ),
    _d("daily", "wetBulbAvg", "wet bulb average", TEMP, _T),
    _d("daily", "wetBulbMax", "wet bulb max", TEMP, _T),
    _d("daily", "wetBulbMin", "wet bulb min", TEMP, _T),
    _d("daily", "windAvgSpeed", "wind average speed", KMH, _W),
    _d("daily", "windMaxSpeed", "wind max speed", KMH, _W),
)


def _api_key(description: DPIRDSensorEntityDescription) -> str:
    """Return the API field name for a description."""
    return description.key.split("_", 1)[1]


def _keys(data_type: str) -> list[str]:
    return [_api_key(d) for d in SENSOR_DESCRIPTIONS if d.data_type == data_type]


LATEST_KEYS = _keys("latest")
DAILY_KEYS = _keys("daily")


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: DPIRDConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DPIRD sensors from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        DPIRDSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class DPIRDSensor(CoordinatorEntity["DPIRDCoordinator"], SensorEntity):
    """A DPIRD weather station sensor."""

    entity_description: DPIRDSensorEntityDescription
    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: DPIRDCoordinator,
        entry: DPIRDConfigEntry,
        description: DPIRDSensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        station = coordinator.station_code
        self._attr_unique_id = f"{station}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, station)},
            name=entry.data.get(CONF_STATION_NAME, station),
            manufacturer="DPIRD",
            model=f"Weather station {station}",
        )

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        bucket = (self.coordinator.data or {}).get(self.entity_description.data_type)
        if not bucket:
            return None
        value = bucket.get(_api_key(self.entity_description))
        # Some API fields are wrapped, e.g. {"value": 12.3}
        if isinstance(value, dict):
            value = value.get("value")
        return value
