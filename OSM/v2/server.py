from osmnx import graph
from shapely.geometry import Point
import networkx as nx
import osmnx as ox
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
all_persons = []
user_location = {}

SIMULATION_RUNNING = True
ofstv = 0.0005

LAT_RANGE = (35.95, 35.98)   # Example: Mehestan, Iran
LNG_RANGE = (50.72, 50.75)

MIN_DISTANCE = 0.0001
MIN_DISTANCE_UNIQUE = 0.00001
DISTANCE_THRESHOLD_METERS = 500

place = "Mehestan, Alborz Province, Iran"
G = ox.graph_from_place(place, network_type="walk")
GC = ox.graph_from_place(place, network_type="drive")


def snap_to_nearest_road(lat, lng, network_type='walk'):
    try:
        nearest_node = ox.distance.nearest_nodes(G, lng, lat)
        snapped_point = G.nodes[nearest_node]
        return {'lat': snapped_point['y'], 'lng': snapped_point['x']}
    except Exception as e:
        print(f"Snap failed: {e}")
        return {'lat': lat, 'lng': lng}  # Fallback


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


def get_offset_patterns(ofst):
    offset_patterns = [
        [-ofst, ofst, -ofst, ofst],
        [ofst, ofst, ofst, ofst],
        [-ofst, -ofst, -ofst, -ofst],
        [ofst, -ofst, ofst, -ofst],
        [0, ofst, 0, ofst],
        [ofst, 0, ofst, 0],
        [-ofst, 0, -ofst, 0],
        [0, -ofst, 0, -ofst],
    ]
    return offset_patterns


def start_simulation():
    def simulation_loop():
        cnt = 0
        global ofstv, SIMULATION_RUNNING, prev_locations, all_persons
        increaseby = 0.0001
        pnum = 5

        while SIMULATION_RUNNING:
            if not user_locations:
                socketio.sleep(1)
                continue

            offset_patterns = get_offset_patterns(ofstv)

            user = user_locations[0]
            lat_o, lng_o = user['originlat'], user['originlng']
            lat_d, lng_d = user['destinationlat'], user['destinationlng']

            offsets = offset_patterns[cnt % len(offset_patterns)]
            candidate_origin = snap_to_nearest_road(
                lat_o + offsets[0], lng_o + offsets[1])
            candidate_destination = snap_to_nearest_road(
                lat_d + offsets[2], lng_d + offsets[3])

            person = {
                "origin": candidate_origin,
                "destination": candidate_destination
            }

            if is_far_enough(candidate_origin, all_persons + [user_location]) and \
               is_far_enough(candidate_destination, all_persons + [user_location]):
                all_persons.append(person)
                socketio.emit('add_person', person)

            cnt += 1
            if cnt % len(offset_patterns) == 0:
                ofstv += increaseby
            if cnt >= pnum * len(offset_patterns):
                print(all_persons)
                SIMULATION_RUNNING = False
                closest_users()
                return

            # socketio.sleep(0.1)

    thread = threading.Thread(target=simulation_loop)
    thread.daemon = True
    thread.start()


def closest_users():
    def get_node(lat, lng):
        return ox.distance.nearest_nodes(G, lng, lat)

    user = user_locations[0]
    lat_o, lng_o = user['originlat'], user['originlng']
    lat_d, lng_d = user['destinationlat'], user['destinationlng']
    origin_main = get_node(lat_o, lng_o)
    destination_main = get_node(lat_d, lng_d)

    distances = []

    # Calculate distance for each user (excluding main)
    for idx in range(len(all_persons)):
        user = all_persons[idx]
        try:
            origin_node = get_node(
                user['origin']['lat'], user['origin']['lng'])
            destination_node = get_node(
                user['destination']['lat'], user['destination']['lng'])

            dist_origin = nx.shortest_path_length(
                G, origin_main, origin_node, weight='length')
            dist_dest = nx.shortest_path_length(
                G, destination_main, destination_node, weight='length')
            total_dist = dist_origin + dist_dest

            distances.append((idx, total_dist))
        except nx.NetworkXNoPath:
            continue  # skip unreachable users

    # Sort users by distance and pick two closest
    distances.sort(key=lambda x: x[1])
    closest_indices = [i for i, _ in distances[:2]]

    # Extract users and delete them from original list
    selected_users = [all_persons[i] for i in closest_indices]

    # Remove selected users (highest index first to avoid shifting)
    for i in sorted(closest_indices, reverse=True):
        del all_persons[i]

    socketio.emit('notify_user', selected_users[0])
    socketio.emit('notify_user', selected_users[1])
    socketio.emit('close_people_found', selected_users)


def find_best_shared_location(latlngs):
    nodes = [ox.distance.nearest_nodes(
        G, loc['lng'], loc['lat']) for loc in latlngs]

    total_dist = {node: 0.0 for node in G.nodes}

    for n in nodes:
        dist_map = nx.single_source_dijkstra_path_length(G, n, weight="length")
        for target_node, dist in dist_map.items():
            total_dist[target_node] += dist

    best_node = min(total_dist, key=total_dist.get)

    return {'lat': G.nodes[best_node]['y'], 'lng': G.nodes[best_node]['x']}


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


# --------------------
# SocketIO Handlers
# --------------------


@socketio.on('connect')
def on_connect():
    print(f"Client connected: {request.sid}")


@socketio.on('user_location')
def on_user_location(data):
    global user_location
    lat_o, lng_o = data['originlat'], data['originlng']
    lat_d, lng_d = data['destinationlat'], data['destinationlng']
    user_location = {'origin': {'lat': lat_o, 'lng': lng_o},
                     'destination': {'lat': lat_d, 'lng': lng_d}}
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
    shared_origin = find_best_shared_location(origins)
    shared_destination = find_best_shared_location(destinations)

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


@app.route('/')
def index():
    return render_template('server_map.html')


# --------------------
# App Runner
# --------------------
if __name__ == '__main__':
    start_simulation()
    socketio.run(app, host='0.0.0.0', port=5001)
