import threading
import time
import requests
from geopy.distance import geodesic

LATITUDE = 41.979654145979715
LONGITUDE = -87.90363070440677
RADIUS = 5
POLL_INTERVAL = 8  # seconds between API calls

latest_data = {"planes": [], "updated_at": None}
_data_lock = threading.Lock()
_started = False


def fetch_aircraft():
    url = f"https://api.adsb.lol/v2/lat/{LATITUDE}/lon/{LONGITUDE}/dist/{RADIUS}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    planes = []
    for plane in response.json().get("ac", []):
        if "lat" not in plane or "lon" not in plane:
            continue
        distance = geodesic((LATITUDE, LONGITUDE), (plane["lat"], plane["lon"])).nautical

        # Only keep the fields the table needs, and force safe types
        clean_plane = {
            "flight": str(plane.get("flight", "")).strip(),
            "lat": plane["lat"],
            "lon": plane["lon"],
            "alt_baro": plane.get("alt_baro", ""),
            "distance_from_source": round(distance, 2),
        }
        
        planes.append(clean_plane)

    return sorted(planes, key=lambda x: x["distance_from_source"])


def _poll_loop():
    while True:
        planes = fetch_aircraft()
        if planes is not None:
            with _data_lock:
                latest_data["planes"] = planes
                latest_data["updated_at"] = time.strftime("%H:%M:%S")
        time.sleep(POLL_INTERVAL)


def get_latest():
    """Thread-safe read of the current snapshot."""
    with _data_lock:
        return list(latest_data["planes"]), latest_data["updated_at"]


def start_polling():
    """Starts the background thread exactly once, even if called multiple times."""
    global _started
    if not _started:
        threading.Thread(target=_poll_loop, daemon=True).start()
        _started = True