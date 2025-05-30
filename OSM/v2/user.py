import socketio as sio_client
from flask import Flask, render_template, request
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

place = "Mehestan, Alborz Province, Iran"

friends = []

# Connect to the server backend
server_socket = sio_client.Client()
server_socket.connect("http://localhost:5001")


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


@socketio.on('join')
def on_join(data):
    sid = request.sid
    join_room(sid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
