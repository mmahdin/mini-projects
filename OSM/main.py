import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

# Load walkable street network
place = "Mehestan, Alborz Province, Iran"
G = ox.graph_from_place(place, network_type="walk")

# Define the three people's positions (latitude, longitude)
locations = [
    (35.968697, 50.735140),  # Person 1
    (35.967553, 50.737248),  # Person 2
    (35.966867, 50.739117),  # Person 3
]

# Get nearest nodes in the graph
orig_nodes = [ox.distance.nearest_nodes(G, lon, lat) for lat, lon in locations]

# Find optimal meeting point (node with minimal total walking distance)
total_distances = {}
for node in G.nodes:
    total_distance = sum(
        nx.shortest_path_length(G, source=orig, target=node, weight="length")
        for orig in orig_nodes
    )
    total_distances[node] = total_distance

best_node = min(total_distances, key=total_distances.get)

# Get lat/lon for all four points
coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in orig_nodes]
best_coords = (G.nodes[best_node]['y'], G.nodes[best_node]['x'])

# Compute bounding box for zooming in (min/max lat/lon of people's positions)
lats, lons = zip(*locations)
min_lat, max_lat = min(lats), max(lats)
min_lon, max_lon = min(lons), max(lons)

# Add some padding to the bounding box to make the plot less cramped
padding = 0.001  # Adjust padding to zoom in or out
min_lat -= padding
max_lat += padding
min_lon -= padding
max_lon += padding

# Plot the graph and routes
routes = [
    nx.shortest_path(G, source=orig, target=best_node, weight="length")
    for orig in orig_nodes
]

fig, ax = ox.plot_graph_routes(
    G, routes, route_linewidth=2, node_size=0, show=False, close=False)

# Plot original positions (3 people)
for i, (lat, lon) in enumerate(coords):
    ax.plot(lon, lat, marker='o', color='blue',
            markersize=10, label=f'Person {i+1}')

# Plot optimal meeting point
ax.plot(best_coords[1], best_coords[0], marker='*',
        color='green', markersize=10, label='Meeting Point')

# Set axis limits to zoom in on the area of interest
ax.set_xlim(min_lon, max_lon)
ax.set_ylim(min_lat, max_lat)

# Add legend and show the plot
ax.legend()
plt.show()
