import numpy as np
import openrouteservice
from itertools import product
from openrouteservice.distance_matrix import distance_matrix
import os
import math
import time
import json
import random
import threading
import requests

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")


with open('api_key', 'r') as f:
    ORS_API_KEY = f.readline()
client = openrouteservice.Client(key=ORS_API_KEY)

# Disable system proxy settings to avoid network interference
for key in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"]:
    os.environ[key] = ""


user_locations = []
simulated_people = []
found_close_people = []
prev_locations = []

SIMULATION_RUNNING = True
ofstv = 0.0005

LAT_RANGE = (35.95, 35.98)   # Example: Mehestan, Iran
LNG_RANGE = (50.72, 50.75)

MIN_DISTANCE = 0.0005
MIN_DISTANCE_UNIQUE = 0.00001
DISTANCE_THRESHOLD_METERS = 500


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

            socketio.sleep(0.1)

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
    locations = data['others'] + [data['user']]

    # Separate origins and destinations
    origins = [loc['origin'] for loc in locations]
    destinations = [loc['destination'] for loc in locations]

    # Find shared origin and destination
    shared_origin = find_best_shared_location(origins, client)
    shared_destination = find_best_shared_location(destinations, client)

    # Build routing data
    user_to_shared_origin = []
    user_to_shared_destination = []

    for idx, loc in enumerate(locations):
        # Route from user origin to shared origin
        route_to_origin = get_route(client, loc['origin'], shared_origin)
        user_to_shared_origin.append({
            'user_id': idx,
            'from': loc['origin'],
            'to': shared_origin,
            'geometry': route_to_origin['geometry'],
            'distance': route_to_origin['distance'],
            'duration': route_to_origin['duration']
        })

        # Route from user destination to shared destination
        route_to_dest = get_route(
            client, loc['destination'], shared_destination)
        user_to_shared_destination.append({
            'user_id': idx,
            'from': loc['destination'],
            'to': shared_destination,
            'geometry': route_to_dest['geometry'],
            'distance': route_to_dest['distance'],
            'duration': route_to_dest['duration']
        })

    # Route between shared origin and destination
    shared_route = get_route(client, shared_origin, shared_destination)

    # Emit all routes to frontend
    emit('routing', {
        'shared_origin': shared_origin,
        'shared_destination': shared_destination,
        'routes': {
            'user_to_shared_origin': user_to_shared_origin,
            'user_to_shared_destination': user_to_shared_destination,
            'shared_origin_to_shared_destination': {
                'from': shared_origin,
                'to': shared_destination,
                'geometry': shared_route['geometry'],
                'distance': shared_route['distance'],
                'duration': shared_route['duration']
            }
        }
    })


def snap_to_road(lng, lat, client):
    try:
        # Use a dummy route to self — ORS will snap this point to the road
        route = client.directions(
            coordinates=[[lng, lat], [lng, lat]],
            profile='foot-walking',
            format='geojson'
        )
        snapped_coords = route['features'][0]['geometry']['coordinates'][0]
        return {'lat': snapped_coords[1], 'lng': snapped_coords[0]}
    except Exception as e:
        print("Snap to road failed using directions:", e)
        return {'lat': lat, 'lng': lng}


def generate_candidate_points(coords, grid_size=3, radius=0.005):
    # Compute center of points
    avg_lat = np.mean([c['lat'] for c in coords])
    avg_lng = np.mean([c['lng'] for c in coords])

    # Create grid of candidate points around center
    offsets = np.linspace(-radius, radius, grid_size)
    candidates = []
    for dlat, dlng in product(offsets, offsets):
        candidates.append({'lat': avg_lat + dlat, 'lng': avg_lng + dlng})
    return candidates


def total_walking_distance(candidate, points, client):
    # Prepare matrix request (from points to candidate)
    try:
        locations = [(p['lng'], p['lat']) for p in points] + \
            [(candidate['lng'], candidate['lat'])]
        sources = list(range(len(points)))         # user points
        destinations = [len(points)]               # the candidate
        matrix = client.distance_matrix(
            locations=locations,
            profile='foot-walking',
            metrics=['distance'],
            sources=sources,
            destinations=destinations
        )
        return sum(matrix['distances'][i][0] for i in range(len(points)))
    except Exception as e:
        print(f"Matrix failed for {candidate}: {e}")
        return float('inf')


def find_best_shared_location(points, client):
    # Snap input points to road
    snapped_points = [snap_to_nearest_road(p['lat'], p['lng']) for p in points]

    # Generate candidates around their average center
    candidates = generate_candidate_points(
        snapped_points, grid_size=5, radius=0.0005)  # tune as needed

    # Snap candidates to road
    snapped_candidates = [snap_to_nearest_road(
        c['lat'], c['lng']) for c in candidates]

    # Evaluate each candidate
    best_candidate = None
    min_total_distance = float('inf')
    print("walking distance")
    for candidate in snapped_candidates:
        total_dist = total_walking_distance(candidate, snapped_points, client)
        if total_dist < min_total_distance:
            min_total_distance = total_dist
            best_candidate = candidate

    return best_candidate


def get_route(client, origin, destination):
    response = client.directions(
        coordinates=[[origin['lng'], origin['lat']], [
            destination['lng'], destination['lat']]],
        profile='foot-walking',
        format='geojson'
    )

    features = response.get('features', [])
    if not features:
        print(f"Empty features for route from {origin} to {destination}")
        return {
            'geometry': [],
            'distance': 0,
            'duration': 0
        }

    feature = features[0]
    summary = feature.get('properties', {}).get('summary', {})
    return {
        'geometry': feature['geometry']['coordinates'],
        'distance': summary.get('distance', 0),
        'duration': summary.get('duration', 0)
    }


@app.route('/')
def index():
    return render_template('server_map.html')


# --------------------
# App Runner
# --------------------
if __name__ == '__main__':
    start_simulation()
    socketio.run(app, host='0.0.0.0', port=5001)
