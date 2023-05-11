import osmnx
import requests
import random

from networkx import MultiDiGraph
from osmnx import settings, projection, distance

import custom_nearest_edge as cne


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
    nearest_edges = [cne.nearest_edges(geom, rtree, coordinate["lat"], coordinate["long"]) for coordinate in
                     coordinates]

    # lats = [coordinate["lat"] for coordinate in coordinates]
    # longs = [coordinate["long"] for coordinate in coordinates]
    # nearest_edges = osmnx.distance.nearest_edges(map, lats, longs)

    nearest_edges = ordered_unique_list(nearest_edges)
    data = [map.get_edge_data(u, v, key) for u, v, key in nearest_edges]

    """
    Notes for processing this data:
    - The edges are ordered and unique
    - Some of the included edges "stick out"  of the actual route due to
        the coordinates being closest to that edge on the crossroads
    - Some edges have multiple streets in them, which can mean multiple highway types
    - Segments with "junktion":"roundabout" tend to have disconnected segments 
    """

    print(data)





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
