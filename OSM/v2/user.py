import socketio as sio_client
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
from itertools import combinations
import math
import threading
import networkx as nx
import osmnx as ox
import requests
import os

# Disable proxies if inherited from environment
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["ALL_PROXY"] = ""
os.environ["all_proxy"] = ""


# Application setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

friends = []

# Connect to the server backend
server_socket = sio_client.Client()
server_socket.connect("http://localhost:5001")

place = "Mehestan, Alborz Province, Iran"
G = ox.graph_from_place(place, network_type="walk")


@app.route('/')
def index():
    return render_template('user_map.html')


@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    print(f"Client disconnected: {sid}")


@socketio.on('apply_request')
def handle_apply_request(data):
    sid = request.sid
    origin = (data['origin']['lat'], data['origin']['lng'])
    destination = (data['destination']['lat'], data['destination']['lng'])

    origin = snap_to_nearest_road(origin[0], origin[1])
    destination = snap_to_nearest_road(destination[0], destination[1])

    origin = (origin['lat'], origin['lng'])
    destination = (destination['lat'], destination['lng'])

    server_socket.emit('user_location', {
                       "originlat": origin[0], "originlng": origin[1], "destinationlat": destination[0], "destinationlng": destination[1]})

    socketio.emit('group_assigned', 'payload')


@server_socket.on('notify_user')
def handle_notify_user_from_server(data):
    print("Received from server:", data)
    socketio.emit('notify_user', data)


@server_socket.on('close_people_found')
def handle_confirm(data):
    global friends
    friends = data
    socketio.emit('ask_for_confirm')


@socketio.on('regroup_request')
def handle_apply_request(markerData):
    server_socket.emit('regroup_request', markerData)


@socketio.on('confirm_request')
def handle_apply_request(markerData):
    server_socket.emit('confirm_request', markerData)


@server_socket.on('routing')
def handle_routing(data):
    socketio.emit('routing', data)


@socketio.on('join')
def on_join(data):
    sid = request.sid
    join_room(sid)


def snap_to_nearest_road(lat, lng):
    try:
        nearest_node = ox.distance.nearest_nodes(G, lng, lat)
        snapped_point = G.nodes[nearest_node]
        return {'lat': snapped_point['y'], 'lng': snapped_point['x']}
    except Exception as e:
        print(f"Snap failed: {e}")
        return None


@socketio.on('snap_to_road')
def handle_snap_to_road(data):
    lat = data.get('lat')
    lng = data.get('lng')

    if lat is None or lng is None:
        emit('snap_error', 'Missing coordinates')
        return

    snapped = snap_to_nearest_road(lat, lng)

    if snapped:
        emit('snapped_coordinates', snapped)
    else:
        emit('snap_error', 'Failed to snap to road')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
