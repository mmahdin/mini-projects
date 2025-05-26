import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

# 1. Load walkable street network
place = "Mehestan, Alborz Province, Iran"
G = ox.graph_from_place(place, network_type="walk")

# 2. Define the three people's positions (lat, lon)
locations = [
    (35.968697, 50.735140),  # Person 1
    (35.967553, 50.737248),  # Person 2
    (35.966867, 50.739117),  # Person 3
]

# 3. Snap each person to the nearest graph node
orig_nodes = [
    ox.distance.nearest_nodes(G, lon, lat)
    for lat, lon in locations
]

# 4. Single‐source Dijkstra from each origin and accumulate total distances
total_dist = {node: 0.0 for node in G.nodes()}
for orig in orig_nodes:
    dist_map = nx.single_source_dijkstra_path_length(G, orig, weight="length")
    for node, d in dist_map.items():
        total_dist[node] += d

# 5. Pick the best meeting node
best_node = min(total_dist, key=total_dist.get)

# 6. Prepare coords for plotting
person_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in orig_nodes]
best_coord = (G.nodes[best_node]['y'], G.nodes[best_node]['x'])

# 7. Build routes
routes = [
    nx.shortest_path(G, source=orig, target=best_node, weight="length")
    for orig in orig_nodes
]

# 8. Plot
fig, ax = ox.plot_graph_routes(
    G, routes, route_linewidth=2, node_size=0, show=False, close=False
)

# Plot each person
for i, (lat, lon) in enumerate(person_coords):
    ax.plot(lon, lat, "o", color="blue", markersize=8, label=f"Person {i+1}")

# Plot meeting point
ax.plot(best_coord[1], best_coord[0], "*", color="green", markersize=12,
        label="Optimal Meeting Point")

# --- Apply axis limits to zoom in around people ---
lats, lons = zip(*person_coords)
min_lat, max_lat = min(lats), max(lats)
min_lon, max_lon = min(lons), max(lons)
padding = 0.001  # adjust for more/less zoom

ax.set_xlim(min_lon - padding, max_lon + padding)
ax.set_ylim(min_lat - padding, max_lat + padding)

# Finalize
ax.legend()
plt.show()
