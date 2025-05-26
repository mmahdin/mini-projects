import streamlit as st
from streamlit_folium import st_folium
import folium
import osmnx as ox
import networkx as nx

# Initialize session state
if 'selected_locations' not in st.session_state:
    st.session_state.selected_locations = []
if 'meeting_point' not in st.session_state:
    st.session_state.meeting_point = None
if 'routes' not in st.session_state:
    st.session_state.routes = None

# Define the place
place = "Mehestan, Alborz Province, Iran"

# Cache the graph loading function


@st.cache_data
def load_graph(place):
    return ox.graph_from_place(place, network_type="walk")


# Create and configure the map
m = folium.Map(
    location=[35.968, 50.737],
    zoom_start=15,
    tiles='OpenStreetMap'
)

# Add custom CSS to change cursor when hovering over map
folium.Element(
    '<style>.leaflet-container { cursor: crosshair !important; }</style>'
).add_to(m.get_root().header)

# Add markers for selected locations
for i, loc in enumerate(st.session_state.selected_locations):
    folium.Marker(
        location=loc,
        popup=f"Person {i+1}",
        icon=folium.Icon(color='blue')
    ).add_to(m)

# Add meeting point and routes if calculated
if st.session_state.meeting_point:
    folium.Marker(
        location=st.session_state.meeting_point,
        popup="Meeting Point",
        icon=folium.Icon(color='green')
    ).add_to(m)
    for route in st.session_state.routes:
        folium.PolyLine(
            locations=route,
            color='blue',
            weight=2
        ).add_to(m)

# Adjust map bounds only when meeting point is calculated
if st.session_state.meeting_point:
    all_points = st.session_state.selected_locations + \
        [st.session_state.meeting_point]
    min_lat = min(p[0] for p in all_points)
    max_lat = max(p[0] for p in all_points)
    min_lon = min(p[1] for p in all_points)
    max_lon = max(p[1] for p in all_points)
    m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

# Display the map and capture clicks
st.write("Click on the map to select up to 3 locations")
clicked = st_folium(m, width=700, height=500)

# Handle map clicks
if clicked and clicked['last_clicked'] and len(st.session_state.selected_locations) < 3:
    lat, lon = clicked['last_clicked']['lat'], clicked['last_clicked']['lng']
    st.session_state.selected_locations.append((lat, lon))
    st.rerun()

# Calculate meeting point when 3 locations are selected
if len(st.session_state.selected_locations) == 3 and st.session_state.meeting_point is None:
    with st.spinner("Calculating optimal meeting point..."):
        G = load_graph(place)
        # Snap locations to nearest nodes
        orig_nodes = [
            ox.distance.nearest_nodes(G, lon, lat)
            for lat, lon in st.session_state.selected_locations
        ]
        # Calculate total distances
        total_dist = {node: 0.0 for node in G.nodes()}
        for orig in orig_nodes:
            dist_map = nx.single_source_dijkstra_path_length(
                G, orig, weight="length")
            for node, d in dist_map.items():
                total_dist[node] += d
        # Find best meeting node
        best_node = min(total_dist, key=total_dist.get)
        # Store meeting point coordinates
        st.session_state.meeting_point = (
            G.nodes[best_node]['y'], G.nodes[best_node]['x'])
        # Calculate routes
        routes = [
            nx.shortest_path(G, source=orig, target=best_node, weight="length")
            for orig in orig_nodes
        ]
        # Function to get route geometry

        def get_route_geometry(G, route):
            route_geometry = []
            for i in range(len(route)-1):
                u, v = route[i], route[i+1]
                edge_data = G[u][v][0]  # assuming the first edge if multiple
                if 'geometry' in edge_data:
                    geom = edge_data['geometry']
                    points = [(lat, lon) for lon, lat in geom.coords]
                else:
                    points = [(G.nodes[u]['y'], G.nodes[u]['x']),
                              (G.nodes[v]['y'], G.nodes[v]['x'])]
                if i > 0:
                    # skip the first point to avoid duplicates
                    points = points[1:]
                route_geometry.extend(points)
            return route_geometry
        # Store routes with detailed geometry
        st.session_state.routes = [
            get_route_geometry(G, route) for route in routes]
        st.rerun()

# Display status message
if len(st.session_state.selected_locations) > 0:
    st.write(
        f"Selected {len(st.session_state.selected_locations)}/3 locations")
if st.session_state.meeting_point:
    st.success("Meeting point calculated!")

# Reset button
if st.button("Reset"):
    st.session_state.selected_locations = []
    st.session_state.meeting_point = None
    st.session_state.routes = None
    st.rerun()
