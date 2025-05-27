from flask_socketio import emit
from flask import request
from itertools import combinations
import math
import threading
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import networkx as nx
import osmnx as ox

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Load the OSM graph centered at [35.968, 50.737]
center_point = (35.968, 50.737)
G = ox.graph_from_point(center_point, dist=1000, network_type='drive')

# Functions to find nearest node and median node


def find_nearest_node(lat, lon):
    """
    Given a latitude and longitude, find the nearest OSM node.
    """
    return ox.distance.nearest_nodes(G, lon, lat)


def median_node_for_points(latlons):
    """
    Given a list of (lat, lon) points, find the OSM node that minimizes the sum
    of shortest-path distances to each point's nearest node.
    """
    # Map each point to its nearest OSM node
    user_nodes = [find_nearest_node(lat, lon) for lat, lon in latlons]

    # Compute the node with the minimal sum of shortest-path distances
    best_node = None
    best_sum = float('inf')
    # Precompute shortest paths from each user node
    sp_lengths = []
    for un in user_nodes:
        lengths = nx.single_source_dijkstra_path_length(G, un, weight='length')
        sp_lengths.append(lengths)

    for node in G.nodes:
        total = 0
        for lengths in sp_lengths:
            if node in lengths:
                total += lengths[node]
            # If no path exists, skip this node
        if total < best_sum:
            best_sum = total
            best_node = node

    return best_node, best_sum


# In-memory store for pending users
# List of dicts: {sid, origin: (lat,lon), destination: (lat,lon)}
pending_users = []
lock = threading.Lock()


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    print(f"Client disconnected: {sid}")
    with lock:
        for u in pending_users:
            if u['sid'] == sid:
                pending_users.remove(u)
                break


@socketio.on('apply_request')
def handle_apply_request(data):
    """
    Data = {
      origin: {lat: float, lng: float},
      destination: {lat: float, lng: float}
    }
    """
    sid = request.sid
    origin = (data['origin']['lat'], data['origin']['lng'])
    destination = (data['destination']['lat'], data['destination']['lng'])

    # Add to pending
    with lock:
        # Remove duplicate SIDs
        pending_users[:] = [u for u in pending_users if u['sid'] != sid]
        pending_users.append({
            'sid': sid,
            'origin': origin,
            'destination': destination,
        })

        if len(pending_users) < 3:
            emit('please_wait', {'msg': 'Please wait for companions...'})
            return

        # Find closest 3 users by average Euclidean distance
        def euclid(a, b):
            return math.hypot(a[0] - b[0], a[1] - b[1])

        best_group = None
        best_avg = float('inf')

        for combo in combinations(pending_users, 3):
            coords = [u['origin'] for u in combo]
            dsum = 0
            count = 0
            for i in range(3):
                for j in range(i + 1, 3):
                    dsum += euclid(coords[i], coords[j])
                    count += 1
            avg = dsum / count
            if avg < best_avg:
                best_avg = avg
                best_group = combo

        group = list(best_group)
        for u in group:
            pending_users.remove(u)

    # === Use OSMnx to calculate best meeting nodes ===
    place = "Mehestan, Alborz Province, Iran"
    G = ox.graph_from_place(place, network_type="walk")

    # Meeting origin
    latlons_o = [u['origin'] for u in group]
    origin_nodes = [
        ox.distance.nearest_nodes(G, lon, lat) for lat, lon in latlons_o
    ]
    total_dist_o = {node: 0.0 for node in G.nodes}
    for orig in origin_nodes:
        dist_map = nx.single_source_dijkstra_path_length(
            G, orig, weight="length")
        for node, dist in dist_map.items():
            total_dist_o[node] += dist
    meet_o_node = min(total_dist_o, key=total_dist_o.get)
    meet_o_latlon = {
        'lat': G.nodes[meet_o_node]['y'],
        'lng': G.nodes[meet_o_node]['x']
    }

    # Meeting destination
    latlons_d = [u['destination'] for u in group]
    dest_nodes = [
        ox.distance.nearest_nodes(G, lon, lat) for lat, lon in latlons_d
    ]
    total_dist_d = {node: 0.0 for node in G.nodes}
    for dest in dest_nodes:
        dist_map = nx.single_source_dijkstra_path_length(
            G, dest, weight="length")
        for node, dist in dist_map.items():
            total_dist_d[node] += dist
    meet_d_node = min(total_dist_d, key=total_dist_d.get)
    meet_d_latlon = {
        'lat': G.nodes[meet_d_node]['y'],
        'lng': G.nodes[meet_d_node]['x']
    }

    # Broadcast group assignment
    for u in group:
        other_users = [
            {
                'origin': {'lat': v['origin'][0], 'lng': v['origin'][1]},
                'destination': {'lat': v['destination'][0], 'lng': v['destination'][1]}
            }
            for v in group if v['sid'] != u['sid']
        ]

        payload = {
            'station_origin': meet_o_latlon,
            'station_destination': meet_d_latlon,
            'others': other_users
        }
        socketio.emit('group_assigned', payload, room=u['sid'])


@socketio.on('join')
def on_join(data):
    sid = request.sid
    join_room(sid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
