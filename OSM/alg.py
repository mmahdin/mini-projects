import osmnx as ox
import networkx as nx
from collections import defaultdict


def get_nearest_nodes(df, network_type='walk'):
    """
    Find nearest OSM nodes for each point in the DataFrame.

    Args:
        df: DataFrame with 'lat' and 'lon' columns
        network_type: Type of network for OSMNX graph (default: 'walk')

    Returns:
        DataFrame with added 'node' column containing nearest OSM node IDs
    """
    G = ox.graph_from_bbox(
        north=df['lat'].max(),
        south=df['lat'].min(),
        east=df['lon'].max(),
        west=df['lon'].min(),
        network_type=network_type
    )
    df['node'] = ox.distance.nearest_nodes(
        G, X=df['lon'].values, Y=df['lat'].values, return_dist=False
    )
    return df, G


def build_distance_matrix(G, nodes, cutoff=1000):
    """
    Build a distance matrix for the given nodes using Dijkstra's algorithm.

    Args:
        G: OSMNX graph
        nodes: List of unique node IDs
        cutoff: Maximum walking distance in meters (default: 1000)

    Returns:
        Dictionary of dictionaries with walking distances between nodes
    """
    return {
        node: nx.single_source_dijkstra_path_length(
            G, node, cutoff=cutoff, weight='length')
        for node in nodes
    }


def group_nodes_by_walking_distance(nodes, distance_matrix):
    """
    Group nodes into clusters of three based on walking distance.

    Args:
        nodes: List of node IDs
        distance_matrix: Dictionary of walking distances between nodes

    Returns:
        List of groups, each containing three node IDs
    """
    ungrouped = set(nodes)
    groups = []

    while len(ungrouped) >= 3:
        current = ungrouped.pop()
        distances = distance_matrix.get(current, {})
        neighbors = [n for n in sorted(
            distances, key=distances.get) if n in ungrouped]
        if len(neighbors) >= 2:
            group = [current, neighbors[0], neighbors[1]]
            ungrouped -= set(group[1:])
            groups.append(group)

    return groups


def find_central_node(group, distance_matrix):
    """
    Find the node with minimum total walking distance to others in the group.

    Args:
        group: List of node IDs in a group
        distance_matrix: Dictionary of walking distances between nodes

    Returns:
        Node ID of the most central node
    """
    return min(
        group,
        key=lambda candidate: sum(
            distance_matrix.get(candidate, {}).get(other, float('inf'))
            for other in group
        ),
        default=None
    )


def get_meeting_points(df, network_type='walk', cutoff=1000):
    """
    Find optimal meeting points for groups of nearby locations.

    Args:
        df: DataFrame with 'lat' and 'lon' columns
        network_type: Type of network for OSMNX graph (default: 'walk')
        cutoff: Maximum walking distance in meters (default: 1000)

    Returns:
        List of (latitude, longitude) tuples for central meeting points
    """
    # Step 1: Get nearest OSM nodes
    df_with_nodes, G = get_nearest_nodes(df, network_type)

    # Step 2: Build distance matrix for unique nodes
    unique_nodes = df_with_nodes['node'].unique().tolist()
    distance_matrix = build_distance_matrix(G, unique_nodes, cutoff)

    # Step 3: Group nodes by walking distance
    groups = group_nodes_by_walking_distance(unique_nodes, distance_matrix)

    # Step 4: Find central node for each group
    central_nodes = [find_central_node(
        group, distance_matrix) for group in groups]

    # Step 5: Convert central nodes to coordinates
    return [(G.nodes[node]['y'], G.nodes[node]['x']) for node in central_nodes if node is not None]

# Example usage:
# import pandas as pd
# df = pd.DataFrame({'lat': [lat1, lat2, ...], 'lon': [lon1, lon2, ...]})
# meeting_points = get_meeting_points(df)
