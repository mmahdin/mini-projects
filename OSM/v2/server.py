import math
import requests
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
import threading
import time
import json
import os

# Disable proxies if inherited from environment
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["ALL_PROXY"] = ""
os.environ["all_proxy"] = ""

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

# Store received user locations and simulated persons
user_locations = []
simulated_people = []
found_close_people = []

SIMULATION_RUNNING = True

# Bounding box for random locations (example: Mehestan, Iran area)
LAT_RANGE = (35.95, 35.98)
LNG_RANGE = (50.72, 50.75)

MIN_DISTANCE = 0.0005
DISTANCE_THRESHOLD = 0.005
DISTANCE_THRESHOLD_METERS = 500


def is_far_enough(new_loc, existing_locs):
    for person in existing_locs:
        for key in ['origin', 'destination']:
            existing = person[key]
            if abs(new_loc['lat'] - existing['lat']) < MIN_DISTANCE and \
               abs(new_loc['lng'] - existing['lng']) < MIN_DISTANCE:
                return False
    return True


random.seed(42)


def random_location(existing_locs):
    for _ in range(100):  # Try up to 100 times to find a valid location
        candidate = {
            "lat": random.uniform(*LAT_RANGE),
            "lng": random.uniform(*LNG_RANGE)
        }
        if is_far_enough(candidate, existing_locs):
            return candidate
    raise ValueError("Could not find a sufficiently distant location.")


def snap_to_nearest_road(lat, lng):
    url = f"http://router.project-osrm.org/nearest/v1/driving/{lng},{lat}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['waypoints']:
            snapped = data['waypoints'][0]['location']
            return {"lat": snapped[1], "lng": snapped[0]}
    return {"lat": lat, "lng": lng}  # fallback to original if fail


def haversine_distance(lat1, lng1, lat2, lng2):
    # Calculate distance between two lat/lng pairs in degrees
    return math.sqrt((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2)


def get_walking_distance(lat1, lng1, lat2, lng2):
    url = f"http://router.project-osrm.org/route/v1/walking/{lng1},{lat1};{lng2},{lat2}?overview=false"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data['routes']:
        return data['routes'][0]['distance']  # distance in meters
    else:
        return float('inf')  # if routing fails, return "infinite" distance


def is_close_to_user_(origin, destination):
    user = user_locations[0]
    lat_o = user['originlat']
    lng_o = user['originlng']
    lat_d = user['destinationlat']
    lng_d = user['destinationlng']
    if (haversine_distance(origin['lat'], origin['lng'], lat_o, lng_o) < DISTANCE_THRESHOLD) and (haversine_distance(destination['lat'], destination['lng'], lat_d, lng_d) < DISTANCE_THRESHOLD):
        return True
    return False


def is_close_to_user(origin, destination):
    if is_close_to_user_(origin, destination):
        user = user_locations[0]
        origin_distance = get_walking_distance(
            origin['lat'], origin['lng'], user['originlat'], user['originlng'])
        destination_distance = get_walking_distance(
            destination['lat'], destination['lng'], user['destinationlat'], user['destinationlng'])
        return origin_distance < DISTANCE_THRESHOLD_METERS and destination_distance < DISTANCE_THRESHOLD_METERS
    return False


def start_simulation():
    def simulation_loop():
        global SIMULATION_RUNNING
        while SIMULATION_RUNNING:
            if user_locations:
                origin = random_location(simulated_people)
                destination = random_location(simulated_people)

                snapped_origin = snap_to_nearest_road(
                    origin["lat"], origin["lng"])
                snapped_destination = snap_to_nearest_road(
                    destination["lat"], destination["lng"])

                person = {
                    "origin": snapped_origin,
                    "destination": snapped_destination
                }

                # Check proximity to user
                if is_close_to_user(snapped_origin, snapped_destination):
                    found_close_people.append(person)
                    print('notify')
                    socketio.emit('notify_user', person)

                    if len(found_close_people) == 2:
                        SIMULATION_RUNNING = False
                        socketio.emit('close_people_found', found_close_people)
                        simulated_people.append(person)
                        socketio.emit('add_person', person)
                        return

                simulated_people.append(person)
                socketio.emit('add_person', person)
                with open('data.json', 'w') as f:
                    json.dump(simulated_people, f)

            socketio.sleep(0.1)

    thread = threading.Thread(target=simulation_loop)
    thread.daemon = True
    thread.start()


def start_simulation_():
    def simulation_loop_():
        cnt = 0
        ofstv = 0.0005
        ofst = [[-ofstv, ofstv, -ofstv, ofstv], [ofstv, ofstv, ofstv, ofstv],
                [-ofstv, -ofstv, -ofstv, -
                    ofstv], [ofstv, -ofstv, ofstv, -ofstv],
                [0, ofstv, 0, ofstv], [ofstv, 0, ofstv, 0],
                [-ofstv, 0, -ofstv, 0], [0, -ofstv, 0, -ofstv]]
        global SIMULATION_RUNNING
        while SIMULATION_RUNNING:
            if user_locations:
                user = user_locations[0]
                lat_o = user['originlat']
                lng_o = user['originlng']
                lat_d = user['destinationlat']
                lng_d = user['destinationlng']

                prsn1_lat_o = lat_o + ofst[cnt][0]
                prsn1_lng_o = lng_o + ofst[cnt][1]
                prsn1_lat_d = lat_d + ofst[cnt][2]
                prsn1_lng_d = lng_d + ofst[cnt][3]

                snapped_origin = snap_to_nearest_road(
                    prsn1_lat_o, prsn1_lng_o)
                snapped_destination = snap_to_nearest_road(
                    prsn1_lat_d, prsn1_lng_d)

                person = {
                    "origin": snapped_origin,
                    "destination": snapped_destination
                }

                socketio.emit('add_person', person)

                if is_far_enough(snapped_origin, simulated_people) and is_far_enough(snapped_destination, simulated_people):
                    simulated_people.append(person)
                    if len(simulated_people) == 2:
                        socketio.emit('notify_user', person)
                        socketio.emit('close_people_found', simulated_people)
                    elif len(simulated_people) < 2:
                        socketio.emit('notify_user', person)

                if cnt == 7:
                    SIMULATION_RUNNING = False
                    return
                cnt += 1
            socketio.sleep(1)

    thread = threading.Thread(target=simulation_loop_)
    thread.daemon = True
    thread.start()


@socketio.on('user_location')
def handle_user_location(data):
    print("Received user location:", data)
    user_locations.append(data)
    socketio.emit('user_marker', data)


@app.route('/')
def index():
    print('ok')
    return render_template('server_map.html')


@socketio.on('connect')
def handle_connect():
    print(f"Server viewer connected: {request.sid}")


if __name__ == '__main__':
    start_simulation_()
    socketio.run(app, host='0.0.0.0', port=5001)
