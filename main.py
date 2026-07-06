import time
import requests
import json
from flask import Flask, jsonify, render_template
from geopy.distance import geodesic

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Aircraft Tracker</title></head>
    <body>
      <h1>Aircraft Tracker</h1>
      <div id="aircraft-list">Loading...</div>
      <script src="/static/display.js"></script>
    </body>
    </html>
    """


@app.route("/data")
def get_aircraft_data():
    latitude = 41.979654145979715
    longitude = -87.90363070440677
    radius = 5

    url = f"https://api.adsb.lol/v2/lat/{latitude}/lon/{longitude}/dist/{radius}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
    planes = []
    for plane in response.json().get('ac'):
        distance = geodesic((latitude, longitude), (plane['lat'], plane['lon'])).nautical
        plane['distance_from_source'] = distance
        planes.append(plane)

    return sorted(planes, key=lambda x: x['distance_from_source'])

open("aircraft.json", "w").write(json.dumps(get_aircraft_data(), indent=4))