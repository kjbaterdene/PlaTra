# PlaTra

**Pla**ne **Tra**cker: A live dashboard that shows freely available data about the planes flying above and around you.

PlaTra polls an ADS-B feed for aircraft near a fixed location and displays it in a [NiceGUI](https://nicegui.io/) dashboard.

## Features

- **Live aircraft tracking** — Polls [adsb.lol](https://api.adsb.lol/) every 10 seconds for all aircraft within a configurable radius
- **Distance & bearing** — Calculates distance and compass bearing from you, so you can look outside and see the planes
- **Aircraft identification** — Looks up manufacturer, model, engine type, and weight class from a local database
- **Live dashboard UI** — Dark-themed, auto-refreshing web dashboard built with NiceGUI showing the closest plane's details plus a table of other nearby aircraft

## How it works

1. Polls the adsb.lol API for aircraft within `RADIUS` nautical miles of a fixed `LATITUDE`/`LONGITUDE`, filtering out anything on the ground or missing position data.
2. For each aircraft, it computes distance and bearing from your location.
3. Cross-references the aircraft's type code against two local lookup tables to get manufacturer/model/engine details.
4. Results are cached in a memory store.
5. A NiceGUI web app reads from that store every 2 seconds and renders the current closest aircraft plus a live table of nearby traffic.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

Dependencies (see `pyproject.toml`):
- [`nicegui`](https://nicegui.io/) — web dashboard UI
- [`requests`](https://requests.readthedocs.io/) — HTTP calls to the ADS-B API
- [`geopy`](https://geopy.readthedocs.io/) — distance calculations

## Setup

Clone the repo:

```bash
git clone https://github.com/kjbaterdene/PlaTra.git
cd PlaTra
```

Install dependencies with `uv`:

```bash
uv sync
```

## Configuration

Set your reference location and search radius at the top of `main.py` :
(ADSB.lol doesn't like it if you poll more frequently than 10 seconds)
```python
LATITUDE = 41.979654145979715
LONGITUDE = -87.90363070440677
RADIUS = 5          # nautical miles
POLL_INTERVAL = 10  # seconds between API calls
```

## Usage

Run the live dashboard:

```bash
uv run dashboard.py
```

Once running, open the dashboard in your browser at the address NiceGUI prints in the terminal (typically `http://localhost:8080`).

## Data sources

- Live aircraft positions: [adsb.lol](https://api.adsb.lol/) — a free, public, no-API-key ADS-B aggregation API
- Aircraft model/manufacturer data:
    - Extensive (Often incomplete/inaccurate) dataset is from [OpenSky Network](https://opensky-network.org/data/aircraft) and hasn't been updated since August of 2025.
    - Basic (More accurate) dataset is from the [FAA Aircraft Char](https://www.faa.gov/airports/engineering/aircraft_char_database/aircraft_data) database (spreadsheet).

## Notes

- The tracker is centered on a fixed lat/lon rather than your device's live location — update the constants in `main.py` to point it at your own location. This will hopefully change.
- ADS-B coverage depends on receiver density in your area; aircraft without an ADS-B transponder, or outside receiver range, won't appear.
- I hope to make this a docker image once it's in a beta testing stage.
