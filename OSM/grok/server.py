import asyncio
import websockets
import json
import osmnx as ox
import networkx as nx
from itertools import combinations

# Load the street network graph for the area around the center point
center_point = (35.968, 50.737)  # (latitude, longitude)
G = ox.graph_from_point(center_point, dist=1000, network_type='drive')

# Store waiting users: {websocket: {'id': str, 'origin_node': int, 'destination_node': int, 'origin_coord': [lat, lon], 'destination_coord': [lat, lon]}}
waiting_users = {}


async def handler(websocket, path):
    """Handle WebSocket connections and messages."""
    async for message in websocket:
        data = json.loads(message)
        origin_coord = data['origin']  # [lat, lon]
        destination_coord = data['destination']  # [lat, lon]

        # Find nearest nodes in the graph (note: osmnx uses (lon, lat))
        origin_node = ox.nearest_nodes(G, origin_coord[1], origin_coord[0])
        destination_node = ox.nearest_nodes(
            G, destination_coord[1], destination_coord[0])

        # Store user data
        user_data = {
            'id': data['id'],
            'origin_node': origin_node,
            'destination_node': destination_node,
            'origin_coord': origin_coord,
            'destination_coord': destination_coord
        }
        waiting_users[websocket] = user_data

        # Check for group formation
        while len(waiting_users) >= 3:
            group = find_best_group()
            if group:
                group_data = process_group(group)
                # Send group data to all members and remove them from waiting list
                for ws in group:
                    await ws.send(json.dumps({'type': 'group', **group_data}))
                    del waiting_users[ws]
            else:
                break

        # If user is still waiting, send wait message
        if websocket in waiting_users:
            await websocket.send(json.dumps({'type': 'wait'}))


def find_best_group():
    """Find the triplet of users with the smallest sum of pairwise distances between origins."""
    min_sum = float('inf')
    best_group = None
    for ws1, ws2, ws3 in combinations(waiting_users.keys(), 3):
        nodes = [waiting_users[ws1]['origin_node'],
                 waiting_users[ws2]['origin_node'],
                 waiting_users[ws3]['origin_node']]
        # Calculate sum of pairwise distances
        dist_sum = sum(nx.shortest_path_length(G, nodes[i], nodes[j], weight='length')
                       for i in range(3) for j in range(i+1, 3))
        if dist_sum < min_sum:
            min_sum = dist_sum
            best_group = [ws1, ws2, ws3]
    return best_group


def process_group(group):
    """Calculate shared origin and destination for the group."""
    origin_nodes = [waiting_users[ws]['origin_node'] for ws in group]
    destination_nodes = [waiting_users[ws]['destination_node'] for ws in group]
    origins_coords = [waiting_users[ws]['origin_coord'] for ws in group]

    # Shared origin: node minimizing sum of distances to other origins
    shared_origin_node = min(origin_nodes, key=lambda node:
                             sum(nx.shortest_path_length(G, node, other, weight='length')
                                 for other in origin_nodes if other != node))
    # Shared destination: node minimizing sum of distances to other destinations
    shared_destination_node = min(destination_nodes, key=lambda node:
                                  sum(nx.shortest_path_length(G, node, other, weight='length')
                                      for other in destination_nodes if other != node))

    # Convert nodes to coordinates (lat, lon)
    shared_origin_coord = [G.nodes[shared_origin_node]
                           ['y'], G.nodes[shared_origin_node]['x']]
    shared_destination_coord = [
        G.nodes[shared_destination_node]['y'], G.nodes[shared_destination_node]['x']]

    return {
        'groupOrigin': shared_origin_coord,
        'groupDestination': shared_destination_coord,
        'companions': origins_coords  # All three users' origins
    }


# Start the WebSocket server
start_server = websockets.serve(handler, "localhost", 8080)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
