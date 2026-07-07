import threading
import time
import math
import json
import requests
from geopy.distance import geodesic

LATITUDE = 41.979654145979715
LONGITUDE = -87.90363070440677
RADIUS = 5
POLL_INTERVAL = 10  # seconds between API calls

latest_data = {"planes": [], "updated_at": None}
_data_lock = threading.Lock()
_started = False

# Open basic plane data
with open(r"plane_codes/mapped_basic_plane_codes.json", "r") as f:
    BASIC_DB = json.load(f)

# Open extensive plane data
with open(r"plane_codes/extensive_plane_codes.json", "r") as f:
    EXT_DB = json.load(f)


def fetch_local_aircraft():
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
        distance = geodesic(
            (LATITUDE, LONGITUDE), (plane["lat"], plane["lon"])
        ).nautical

        # Calculate bearing
        bearing = compute_bearing(LATITUDE, LONGITUDE, plane["lat"], plane["lon"])

        # Grab data from basic map
        plane_data = fetch_plane_data(plane.get("t", ""))

        # Only save needed data
        clean_plane = {
            "hex": plane.get("hex", ""),
            "flight": str(plane.get("flight", "")).strip(),
            "r": plane.get("r", ""),
            "t": plane.get("t", ""),
            "lat": plane["lat"],
            "lon": plane["lon"],
            "true_heading": plane.get("true_heading", ""),
            "distance_from_source": round(distance, 2),
            "bearing": round(bearing, 1),
            "compass": bearing_to_compass(bearing),
            "plane_data": plane_data
        }
        planes.append(clean_plane)

    return sorted(planes, key=lambda x: x["distance_from_source"])

def compute_bearing(lat1, lon1, lat2, lon2):
    lat1, lat2 = math.radians(lat1), math.radians(lat2)
    diff_lon = math.radians(lon2 - lon1)
    x = math.sin(diff_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(diff_lon)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def bearing_to_compass(bearing):
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[round(bearing / 45) % 8]


def fetch_plane_data(icao):
    if not icao:
        return None
    plane_data = {}
    basic_data = BASIC_DB.get(icao)
    extensive_data = EXT_DB.get(icao)
    if basic_data:
        plane_data['name'] = basic_data["Model_FAA"]
        plane_data['manufacturer'] = basic_data["Manufacturer"]
        plane_data['engine'] = f"{basic_data["Physical_Class_Engine"]} ({basic_data["Num_Engines"]})"
        plane_data['class'] = basic_data["Class"]
        plane_data['Weight'] = basic_data["FAA_Weight"]
    elif extensive_data and extensive_data.get("model"):
        plane_data['name'] = extensive_data["model"]
    
    return plane_data
    

def _poll_loop():
    while True:
        planes = fetch_local_aircraft()
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

if __name__ == "__main__":
    print(fetch_local_aircraft())