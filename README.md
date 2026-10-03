# DPIRD Weather for Home Assistant

A Home Assistant custom integration for the Western Australian Department of Primary
Industries and Regional Development (DPIRD) weather station network, using the
[DPIRD Weather 2.0 API](https://weather.agric.wa.gov.au/developer-api).

## Features

- Choose any open DPIRD weather station from a dropdown when you set up the integration.
- Current observations (temperature, humidity, rainfall, wind, pressure, solar, soil and more).
- Today's daily summary values (min/max/average temperature, rainfall total and more).
- A core set of sensors is enabled by default; the rest can be enabled from the device page.
- Add the integration again to monitor additional stations.

## Installation

### HACS (custom repository)

1. HACS → three-dot menu → **Custom repositories**.
2. Add `https://github.com/mvisic/ha-dpird-weather` with category **Integration**.
3. Download **DPIRD Weather** and restart Home Assistant.

### Manual

Copy `custom_components/dpird_weather` into your Home Assistant `config/custom_components/` folder and restart.

## Setup

1. Request a free API key from the [DPIRD API page](https://weather.agric.wa.gov.au/developer-api).
2. **Settings → Devices & services → Add integration → DPIRD Weather**.
3. Enter your API key, then choose your weather station.

## Data licence

Data is provided by DPIRD under the Creative Commons Attribution 3.0 Australia licence.
See DPIRD's terms and conditions for API use.
