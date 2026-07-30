"""Sensor platform for DPIRD Weather."""
from dataclasses import dataclass
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

@dataclass
class DPIRDSensorEntityDescription:
    """Class describing DPIRD sensor entities."""
    key: str
    name: str
    data_type: str  # "latest" or "daily"
    native_unit_of_measurement: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    icon: str | None = None


# Comprehensive list of all available metrics from Latest and Daily endpoints
SENSOR_DESCRIPTIONS: tuple[DPIRDSensorEntityDescription, ...] = [
    # --- LATEST / CURRENT OBSERVATIONS ---
    DPIRDSensorEntityDescription("airTemperature", "Air Temperature", "latest", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("airTemperatureMinLast24Hrs", "Air Temperature Min Last 24 Hrs", "latest", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("airTemperatureMaxLast24Hrs", "Air Temperature Max Last 24 Hrs", "latest", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("airTemperatureLow6PMto9AM", "Air Temperature Low 6PM to 9AM", "latest", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("airTemperatureHigh6AMto9PM", "Air Temperature High 6AM to 9PM", "latest", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("apparentTemperature", "Apparent Temperature", "latest", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("barometricPressure", "Barometric Pressure", "latest", UnitOfPressure.HPA, SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("batteryVoltage", "Battery Voltage", "latest", "V", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("deltaT", "Delta T", "latest", "°C", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("dewPoint", "Dew Point", "latest", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("etoShortCrop", "Eto Short Crop", "latest", "mm", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("etoTallCrop", "Eto Tall Crop", "latest", "mm", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("etoShortCropTo3PM", "Eto Short Crop to 3PM", "latest", "mm", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("etoTallCropTo3PM", "Eto Tall Crop to 3PM", "latest", "mm", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("panEvaporation", "Pan Evaporation", "latest", "mm", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("panEvaporation12AM", "Pan Evaporation 12AM", "latest", "mm", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("panEvaporationTo3PM", "Pan Evaporation to 3PM", "latest", "mm", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("rainfallSince9AM", "Rainfall Since 9AM", "latest", "mm", SensorDeviceClass.PRECIPITATION, SensorStateClass.TOTAL_INCREASING),
    DPIRDSensorEntityDescription("rainfallTo9AM", "Rainfall to 9AM", "latest", "mm", SensorDeviceClass.PRECIPITATION, SensorStateClass.TOTAL),
    DPIRDSensorEntityDescription("rainfallTo3PM", "Rainfall to 3PM", "latest", "mm", SensorDeviceClass.PRECIPITATION, SensorStateClass.TOTAL),
    DPIRDSensorEntityDescription("relativeHumidity", "Relative Humidity", "latest", "%", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("soilTemperature", "Soil Temperature", "latest", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("solarExposure", "Solar Exposure", "latest", "MJ/m²", SensorDeviceClass.IRRADIANCE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("solarIrradiance", "Solar Irradiance", "latest", "W/m²", SensorDeviceClass.IRRADIANCE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("wetBulb", "Wet Bulb", "latest", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("windAvgSpeed", "Wind Avg Speed", "latest", UnitOfSpeed.METERS_PER_SECOND, SensorDeviceClass.WIND_SPEED, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("windMaxSpeed", "Wind Max Speed", "latest", UnitOfSpeed.METERS_PER_SECOND, SensorDeviceClass.WIND_SPEED, SensorStateClass.MEASUREMENT),

    # --- DAILY SUMMARY STATISTICS ---
    DPIRDSensorEntityDescription("airTemperatureAvg", "Daily Air Temperature Avg", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("airTemperatureMax", "Daily Air Temperature Max", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("airTemperatureMin", "Daily Air Temperature Min", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("apparentAirTemperatureAvg", "Daily Apparent Air Temp Avg", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("apparentAirTemperatureMax", "Daily Apparent Air Temp Max", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("apparentAirTemperatureMin", "Daily Apparent Air Temp Min", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("barometricPressureAvg", "Daily Barometric Pressure Avg", "daily", UnitOfPressure.HPA, SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("barometricPressureMax", "Daily Barometric Pressure Max", "daily", UnitOfPressure.HPA, SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("barometricPressureMin", "Daily Barometric Pressure Min", "daily", UnitOfPressure.HPA, SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("batteryMinVoltage", "Daily Battery Min Voltage", "daily", "V", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("chillHours", "Daily Chill Hours", "daily", "h", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("deltaTAvg", "Daily Delta T Avg", "daily", "°C", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("deltaTMax", "Daily Delta T Max", "daily", "°C", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("deltaTMin", "Daily Delta T Min", "daily", "°C", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("dewPointAvg", "Daily Dew Point Avg", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("dewPointMax", "Daily Dew Point Max", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("dewPointMin", "Daily Dew Point Min", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("evapotranspiration", "Daily Evapotranspiration", "daily", "mm", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("evapotranspirationShortCrop", "Daily Eto Short Crop", "daily", "mm", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("evapotranspirationTallCrop", "Daily Eto Tall Crop", "daily", "mm", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("panEvaporation", "Daily Pan Evaporation", "daily", "mm", None, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("rainfall", "Daily Rainfall Total", "daily", "mm", SensorDeviceClass.PRECIPITATION, SensorStateClass.TOTAL),
    DPIRDSensorEntityDescription("relativeHumidityAvg", "Daily Relative Humidity Avg", "daily", "%", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("relativeHumidityMax", "Daily Relative Humidity Max", "daily", "%", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("relativeHumidityMin", "Daily Relative Humidity Min", "daily", "%", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("soilTemperatureAvg", "Daily Soil Temperature Avg", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("soilTemperatureMax", "Daily Soil Temperature Max", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("soilTemperatureMin", "Daily Soil Temperature Min", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("solarExposure", "Daily Solar Exposure", "daily", "MJ/m²", SensorDeviceClass.IRRADIANCE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("wetBulbAvg", "Daily Wet Bulb Avg", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("wetBulbMax", "Daily Wet Bulb Max", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("wetBulbMin", "Daily Wet Bulb Min", "daily", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("windAvgSpeed", "Daily Wind Avg Speed", "daily", UnitOfSpeed.METERS_PER_SECOND, SensorDeviceClass.WIND_SPEED, SensorStateClass.MEASUREMENT),
    DPIRDSensorEntityDescription("windMaxSpeed", "Daily Wind Max Speed", "daily", UnitOfSpeed.METERS_PER_SECOND, SensorDeviceClass.WIND_SPEED, SensorStateClass.MEASUREMENT),
]


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up all DPIRD sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        DPIRDSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class DPIRDSensor(CoordinatorEntity, SensorEntity):
    """Representation of a DPIRD Sensor."""

    def __init__(self, coordinator, description: DPIRDSensorEntityDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"WA {description.name}"
        self._attr_unique_id = f"dpird_{description.data_type}_{description.key}"
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data_bucket = self.coordinator.data.get(self.entity_description.data_type, {})
        if not data_bucket:
            return None
        return data_bucket.get(self.entity_description.key)
