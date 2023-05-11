import random

import networkx
import osmnx
import requests
from matplotlib import pyplot as plt
from networkx import MultiDiGraph
from osmnx import settings, projection

import helpers.custom_nearest_edge as cne
from src.router_service.models.route_models import Node


def fetch_vehicle_ids():
    url = "http://localhost:5099/getAllVehicleID's"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("No vehicle IDs found")


def fetch_coordinates(vehicle_id):
    url = f"http://localhost:5099/getById?id={vehicle_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"No coordinates found for the vehicle {vehicle_id}")


def init_osmnx(region: str) -> MultiDiGraph:
    """
    Initialize OSMNX with configuration.

    :param region: The region for which to generate a map
    :return osmnx_map: The OSMNX map of the given region as a networkx multidimensional graph
    """
    # Configure osmnx, area and routing settings
    # For settings see https://osmnx.readthedocs.io/en/stable/osmnx.html?highlight=settings#module-osmnx.settings
    settings.log_console = True
    settings.use_cache = True

    # find the shortest route based on the mode of travel
    mode = "drive"  # 'drive', 'bike', 'walk'
    # create graph from OSM within the boundaries of some
    # geocodable place(s)
    osmnx_map = osmnx.graph_from_place(region, network_type=mode)
    osmnx_map = osmnx.projection.project_graph(osmnx_map, to_crs="EPSG:4326")

    return osmnx_map


def map_to_map(map, coordinates):
    """
    Map the given coordinates to the given map.

    :param map: The map to which to map the coordinates
    :param coordinates: The coordinates to map
    :return:
    """
    geom, rtree = cne.init_rtree(map)
    nearest_edges = [cne.nearest_edges(geom, rtree, coordinate["lat"], coordinate["long"])
                     for coordinate in
                     coordinates]

    nearest_edges = ordered_unique_list(nearest_edges)
    data = [map.get_edge_data(u, v, key) for u, v, key in nearest_edges]

    g = networkx.Graph.edge_subgraph(map, nearest_edges)
    networkx.draw(g)
    plt.savefig("base.png", format="PNG")

    extra_edges = []
    for edge in nearest_edges:
        extra_edges.append([edge for edge in map.in_edges(edge[0])])
        extra_edges.append([edge for edge in map.out_edges(edge[0])])
        extra_edges.append([edge for edge in map.in_edges(edge[1])])
        extra_edges.append([edge for edge in map.out_edges(edge[1])])
    extra_edges = [item for sublist in extra_edges for item in sublist]
    extra_edges = [(edge[0], edge[1], 0) for edge in extra_edges]
    extra_edges = ordered_unique_list(extra_edges)

    start = nearest_edges[0][0] if nearest_edges[0][0] in nearest_edges[1] else nearest_edges[0][1]
    end = nearest_edges[-1][0] if nearest_edges[-1][0] in nearest_edges[-2] else nearest_edges[-1][1]

    route = networkx.shortest_path(networkx.Graph.edge_subgraph(map, nearest_edges + extra_edges), start, end)
    # We want: highway, length, name, osmid, end and start node coordinates and ids
    route_nodes, route_edges = osmnx.graph_to_gdfs(map.subgraph(route))
    route_edges = route_edges.reset_index()

    # Sort the route table
    previous_node = None
    for index, node in enumerate(route):
        # Find next node and filter out backwards routes
        route_edges.loc[(route_edges["u"] == node) & ~(route_edges["v"] == previous_node), "order"] = index
        previous_node = node
    route_edges = route_edges.loc[~route_edges["order"].isnull()].sort_values(by=["order"])
    route_edges = route_edges.drop(columns=["order"]).set_index(["u", "v", "key"])

    out = []
    for node in route:
        # For every node: grab that node as "start",
        #   grab the next node as "end",
        #   grab connecting edge as "way"
        # TODO: grab nodes, go through and build the models
        tuple()
        start = Node()
        out.append(route_edges.loc[route_edges['u'] == node | route_edges['v'] == node])

    print("yeet")


def ordered_unique_list(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def run():
    vehicle_ids = fetch_vehicle_ids()
    random_vehicle_id = random.choice(vehicle_ids)
    coordinates = fetch_coordinates(random_vehicle_id)
    map = init_osmnx("Eindhoven, Noord-Brabant, Netherlands")
    map_to_map(map, coordinates)


if __name__ == "__main__":
    """
    Run the service.
    """
    run()
