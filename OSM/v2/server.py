import os
import math
import time
import json
import random
import threading
import requests

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

# --------------------
# Flask & SocketIO Setup
# --------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

# --------------------
# Environment Clean-up
# --------------------
# Disable system proxy settings to avoid network interference
for key in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"]:
    os.environ[key] = ""

# --------------------
# Global State
# --------------------
user_locations = []
simulated_people = []
found_close_people = []
prev_locations = []

SIMULATION_RUNNING = True
ofstv = 0.0005

# --------------------
# Constants
# --------------------
LAT_RANGE = (35.95, 35.98)   # Example: Mehestan, Iran
LNG_RANGE = (50.72, 50.75)

MIN_DISTANCE = 0.0005
MIN_DISTANCE_UNIQUE = 0.00001
DISTANCE_THRESHOLD_METERS = 500

# --------------------
# Utilities
# --------------------


def snap_to_nearest_road(lat, lng):
    url = f"http://router.project-osrm.org/nearest/v1/driving/{lng},{lat}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['waypoints']:
                snapped = data['waypoints'][0]['location']
                return {"lat": snapped[1], "lng": snapped[0]}
    except Exception as e:
        print(f"Snap failed: {e}")
    return {"lat": lat, "lng": lng}  # Fallback


def is_far_enough(new_loc, existing_people):
    for person in existing_people:
        for key in ['origin', 'destination']:
            existing = person[key]
            if abs(new_loc['lat'] - existing['lat']) < MIN_DISTANCE and \
               abs(new_loc['lng'] - existing['lng']) < MIN_DISTANCE:
                return False
    return True


def is_unique(new_loc, existing_people):
    for person in existing_people:
        for key in ['origin', 'destination']:
            existing = person[key]
            if abs(new_loc['lat'] - existing['lat']) < MIN_DISTANCE_UNIQUE and \
               abs(new_loc['lng'] - existing['lng']) < MIN_DISTANCE_UNIQUE:
                return False
    return True

# --------------------
# Simulation Logic
# --------------------


def start_simulation():
    def simulation_loop():
        cnt = 0
        global ofstv, SIMULATION_RUNNING, simulated_people, prev_locations

        offset_patterns = [
            [-ofstv, ofstv, -ofstv, ofstv],
            [ofstv, ofstv, ofstv, ofstv],
            [-ofstv, -ofstv, -ofstv, -ofstv],
            [ofstv, -ofstv, ofstv, -ofstv],
            [0, ofstv, 0, ofstv],
            [ofstv, 0, ofstv, 0],
            [-ofstv, 0, -ofstv, 0],
            [0, -ofstv, 0, -ofstv],
        ]

        while SIMULATION_RUNNING:
            if not user_locations:
                socketio.sleep(1)
                continue

            user = user_locations[0]
            lat_o, lng_o = user['originlat'], user['originlng']
            lat_d, lng_d = user['destinationlat'], user['destinationlng']

            offsets = offset_patterns[cnt]
            candidate_origin = snap_to_nearest_road(
                lat_o + offsets[0], lng_o + offsets[1])
            candidate_destination = snap_to_nearest_road(
                lat_d + offsets[2], lng_d + offsets[3])

            person = {
                "origin": candidate_origin,
                "destination": candidate_destination
            }
            if is_unique(candidate_origin, prev_locations) and \
               is_unique(candidate_destination, prev_locations):
                print('******************')
            if is_unique(candidate_origin, prev_locations) and \
               is_unique(candidate_destination, prev_locations) and \
               is_far_enough(candidate_origin, simulated_people) and \
               is_far_enough(candidate_destination, simulated_people):
                simulated_people.append(person)

                socketio.emit('add_person', person)
                socketio.emit('notify_user', person)

                if len(simulated_people) == 2:
                    socketio.emit('close_people_found', simulated_people)
                    SIMULATION_RUNNING = False
                    simulated_people.clear()
                    return

            cnt += 1
            if cnt >= len(offset_patterns):
                SIMULATION_RUNNING = False
                simulated_people.clear()
                return

            socketio.sleep(1)

    thread = threading.Thread(target=simulation_loop)
    thread.daemon = True
    thread.start()

# --------------------
# SocketIO Handlers
# --------------------


@socketio.on('connect')
def on_connect():
    print(f"Client connected: {request.sid}")


@socketio.on('user_location')
def on_user_location(data):
    print("Received user location:", data)
    user_locations.append(data)
    socketio.emit('user_marker', data)


@socketio.on('regroup_request')
def on_regroup_request(data):
    global SIMULATION_RUNNING, ofstv, prev_locations
    prev_locations += data['others']
    ofstv += 0.00000
    SIMULATION_RUNNING = True
    start_simulation()


@socketio.on('confirm_request')
def on_confirm_request(data):
    all_locs = data['others'] + [data['user']]
    print(all_locs)
    pass
# --------------------
# Routes
# --------------------


@app.route('/')
def index():
    return render_template('server_map.html')


# --------------------
# App Runner
# --------------------
if __name__ == '__main__':
    start_simulation()
    socketio.run(app, host='0.0.0.0', port=5001)
