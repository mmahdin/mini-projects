import math
import threading
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import networkx as nx

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# ------------------------------
# Build a simple grid-based graph around [35.968, 50.737]
# so that we can run Dijkstra on it.
# Nodes will be (i, j) grid indices mapped to lat/lon.
# ------------------------------
CENTER_LAT = 35.968
CENTER_LON = 50.737
GRID_SIZE = 21   # 21x21 grid
DELTA = 0.0005   # approx ~50m per step (very rough)

G = nx.Graph()
node_positions = {}  # maps node -> (lat, lon)

# Create grid nodes
half = GRID_SIZE // 2
for i in range(-half, half + 1):
    for j in range(-half, half + 1):
        lat = CENTER_LAT + i * DELTA
        lon = CENTER_LON + j * DELTA
        node = (i, j)
        node_positions[node] = (lat, lon)
        G.add_node(node)

# Connect 4−neighbors with edge weight = Euclidean distance
for i in range(-half, half + 1):
    for j in range(-half, half + 1):
        node = (i, j)
        for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            ni, nj = i + di, j + dj
            if -half <= ni <= half and -half <= nj <= half:
                neighbor = (ni, nj)
                lat1, lon1 = node_positions[node]
                lat2, lon2 = node_positions[neighbor]
                # very rough distance in degrees (we'll pretend it's linear)
                dist = math.hypot(lat1 - lat2, lon1 - lon2)
                G.add_edge(node, neighbor, weight=dist)

# Precompute a flat list of nodes & positions for nearest-node queries
all_nodes = list(G.nodes)
all_positions = [node_positions[n] for n in all_nodes]


def find_nearest_node(lat, lon):
    """
    Given a lat/lon, find the grid node whose (lat, lon) is closest by Euclidean.
    """
    best = None
    best_dist = float('inf')
    for node, (nlat, nlon) in zip(all_nodes, all_positions):
        d = math.hypot(lat - nlat, lon - nlon)
        if d < best_dist:
            best_dist = d
            best = node
    return best


def median_node_for_points(latlons):
    """
    Given a list of (lat, lon) points, find the single node in G
    that minimizes the sum of shortest-path distances to each point’s nearest node.
    """
    # 1) Map each point to its nearest graph node
    user_nodes = [find_nearest_node(lat, lon) for lat, lon in latlons]

    # 2) For every node in the graph, compute sum of distances to each user_node
    #    Pick the node with minimal sum.
    best_node = None
    best_sum = float('inf')
    # Precompute single‐source shortest paths from each user_node
    sp_lengths = []
    for un in user_nodes:
        lengths = nx.single_source_dijkstra_path_length(G, un, weight='weight')
        sp_lengths.append(lengths)

    for node in G.nodes:
        total = 0
        for lengths in sp_lengths:
            total += lengths[node]
        if total < best_sum:
            best_sum = total
            best_node = node

    return best_node, best_sum


# ------------------------------
# In-memory “pending” store for connected users who have clicked Apply,
# but not yet been grouped into threes.
# ------------------------------
# list of dicts: { sid, origin: (lat,lon), dest: (lat,lon) }
pending_users = []


lock = threading.Lock()


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    # No immediate action; wait for them to send origin/dest via 'apply_request'


@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    print(f"Client disconnected: {sid}")
    with lock:
        # Remove from pending if they were waiting
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
        # First, check if this SID is already in pending (ignore duplicates)
        pending_users[:] = [u for u in pending_users if u['sid'] != sid]
        pending_users.append({
            'sid': sid,
            'origin': origin,
            'destination': destination,
        })

        # If fewer than 3, ask them to wait
        if len(pending_users) < 3:
            emit('please_wait', {'msg': 'Please wait for companions...'})
            return

        # Otherwise, find the three “closest” pending users (by average Euclidean orig‐orig distance)
        # Start by computing pairwise distances between pending origins
        def euclid(a, b):
            return math.hypot(a[0] - b[0], a[1] - b[1])

        best_group = None
        best_avg = float('inf')
        # Try every triple combination of pending_users
        from itertools import combinations
        for combo in combinations(pending_users, 3):
            coords = [u['origin'] for u in combo]
            # compute average pairwise distance
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

        # best_group is a tuple of 3 user‐dicts
        group = list(best_group)

        # Remove these 3 from pending_users
        for u in group:
            pending_users.remove(u)

    # Now, for these three users:
    #   1) Compute “best” meeting origin node via Dijkstra median_node_for_points
    #   2) Compute “best” meeting destination node similarly
    latlons_o = [u['origin'] for u in group]
    latlons_d = [u['destination'] for u in group]

    meet_o_node, _ = median_node_for_points(latlons_o)
    meet_d_node, _ = median_node_for_points(latlons_d)
    meet_o_latlon = {
        'lat': node_positions[meet_o_node][0], 'lng': node_positions[meet_o_node][1]}
    meet_d_latlon = {
        'lat': node_positions[meet_d_node][0], 'lng': node_positions[meet_d_node][1]}

    # Broadcast to each user in the group their “station” plus the other users’ orig/dest
    sids = [u['sid'] for u in group]
    for u in group:
        other_users = []
        for v in group:
            if v['sid'] == u['sid']:
                continue
            other_users.append({
                'origin': {'lat': v['origin'][0], 'lng': v['origin'][1]},
                'destination': {'lat': v['destination'][0], 'lng': v['destination'][1]},
            })

        payload = {
            'station_origin': meet_o_latlon,
            'station_destination': meet_d_latlon,
            'others': other_users
        }
        socketio.emit('group_assigned', payload, room=u['sid'])


@socketio.on('join')
def on_join(data):
    """
    Let the server know which room corresponds to this sid.
    We can just use sid as a “room” so we can send to it directly.
    """
    sid = request.sid
    join_room(sid)


if __name__ == '__main__':
    # Use eventlet for async
    socketio.run(app, host='0.0.0.0', port=5000)
