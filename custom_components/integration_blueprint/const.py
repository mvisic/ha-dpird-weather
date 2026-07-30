"""Constants for the DPIRD Weather integration."""
DOMAIN = "dpird_weather"
API_LATEST = "https://api.agric.wa.gov.au/v2/weather/stations/{station}/latest?select=airTemperature,apparentTemperature,rainfallSince9AM,relativeHumidity,soilTemperature,soilTemperatureMin,soilTemperatureMax,solarExposure,wind"
API_DAILY = "https://api.agric.wa.gov.au/v2/weather/stations/summaries/daily?startDate={date}&endDate={date}&stationCode={station}&offset=0&limit=25&select=soilTemperatureAvg,soilTemperatureMax,soilTemperatureMin&includeClosed=false"
