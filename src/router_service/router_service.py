"""
Router service.
"""
import random
import uuid

import helpers.custom_nearest_edge as cne
import networkx
import osmnx
import pandas
import requests
from networkx import MultiDiGraph
from osmnx import projection, settings
from src.router_service.models.route_models import Node, Route, Segment, Way


def fetch_vehicle_ids():
    """
    Fetch vehicle ids from the router API.
    """
    url = "http://localhost:5099/getAllVehicleID's"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("No vehicle IDs found")


def fetch_coordinates(vehicle_id):
    """
    Fetch coordinates for the given vehicle from the router API.
    """
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
    osmnx_map = projection.project_graph(osmnx_map, to_crs="EPSG:4326")

    return osmnx_map


def map_to_map(area_graph: MultiDiGraph, coordinates: list):
    """
    Map the given coordinates to the given map.

    :param area_graph: The graph of the area to which to map the coordinates
    :param coordinates: The coordinates to map
    :return:
    """
    geom, rtree = cne.init_rtree(area_graph)
    # Get a list of edges that are the nearest to the given coordinates
    nearest_edges = [
        cne.nearest_edges(geom, rtree, coordinate["lat"], coordinate["long"])
        for coordinate in coordinates
    ]
    nearest_edges = ordered_unique_list(nearest_edges)

    # Determine the start and end of the route
    start = (
        nearest_edges[0][0]
        if nearest_edges[0][0] in nearest_edges[1]
        else nearest_edges[0][1]
    )
    end = (
        nearest_edges[-1][0]
        if nearest_edges[-1][0] in nearest_edges[-2]
        else nearest_edges[-1][1]
    )

    # Fill in the gaps between the nearest edges by adding all connected edges
    extra_edges = fill_edge_gaps(area_graph, nearest_edges)

    # Find the shortest route between the start and end using the filled graph
    route_node_ids = networkx.shortest_path(
        networkx.Graph.edge_subgraph(area_graph, nearest_edges + extra_edges),
        start,
        end,
    )

    # Get the route edges and nodes tables
    route_edges, route_nodes = get_sorted_route_df(area_graph, route_node_ids)

    # Create the route object from the tables
    return generate_formatted_route(route_node_ids, route_edges, route_nodes)


def fill_edge_gaps(area_graph: MultiDiGraph, nearest_edges: list) -> list:
    """
    Fill in the gaps between the nearest edges by adding all connected edges.

    :param area_graph: The graph of the area to which to map the coordinates
    :param nearest_edges: The edges that are the nearest to the given coordinates
    :return:
    """
    extra_edges = []
    for edge in nearest_edges:
        extra_edges.append(list(area_graph.in_edges(edge[0])))
        extra_edges.append(list(area_graph.out_edges(edge[0])))
        extra_edges.append(list(area_graph.in_edges(edge[1])))
        extra_edges.append(list(area_graph.out_edges(edge[1])))
    extra_edges = [item for sublist in extra_edges for item in sublist]
    extra_edges = [(edge[0], edge[1], 0) for edge in extra_edges]
    extra_edges = ordered_unique_list(extra_edges)
    return extra_edges


def get_sorted_route_df(
    area_graph: MultiDiGraph, route_node_ids: list
) -> (pandas.DataFrame, pandas.DataFrame):
    """
    Generate the route edges and nodes tables.

    Edges are sorted in the order their nodes appear in route.
    Nodes are not sorted.

    :param area_graph: The map to which the route is mapped
    :param route_node_ids: The route to be mapped in the form of an ordered list of nodes.
    :return: The route edges and nodes tables.
    """
    route_nodes, route_edges = osmnx.graph_to_gdfs(area_graph.subgraph(route_node_ids))
    route_edges = route_edges.reset_index()
    # Sort the route table
    previous_node = None
    for index, node in enumerate(route_node_ids):
        # Find next node and filter out backwards routes
        route_edges.loc[
            (route_edges["u"] == node) & ~(route_edges["v"] == previous_node), "order"
        ] = index
        previous_node = node
    route_edges = route_edges.loc[~route_edges["order"].isnull()].sort_values(
        by=["order"]
    )
    route_edges = route_edges.drop(columns=["order"]).set_index(["u", "v", "key"])
    return route_edges, route_nodes


def generate_formatted_route(
    route: list, route_edges: pandas.DataFrame, route_nodes: pandas.DataFrame
) -> Route:
    """
    Generate a route using the Route model as specified in the route_models.

    :param route: List of ordered nodes in the route.
    :param route_edges: Dataframe containing the edges of the route in order.
    :param route_nodes: Dataframe containing the nodes of the route.
    :return: The route as a Route model.

    """
    out = Route(route_id=uuid.uuid4())
    for index, node in enumerate(route[:-2]):
        next_node = route[index + 1]
        start_data = route_nodes.loc[node, ["lon", "lat"]].to_dict()
        end_data = route_nodes.loc[next_node, ["lon", "lat"]].to_dict()
        way_data = route_edges.iloc[index].fillna("").to_dict()

        out.add_segment(
            Segment(
                start=Node(osmid=node, lon=start_data["lon"], lat=start_data["lat"]),
                way=Way(
                    osmid=way_data["osmid"],
                    name=way_data["name"],
                    highway=way_data["highway"],
                    length=way_data["length"],
                ),
                end=Node(osmid=next_node, lon=end_data["lon"], lat=end_data["lat"]),
            )
        )
    return out


def ordered_unique_list(seq):
    """
    Return a list with unique elements in the order they appear in the sequence.

    :param seq: The sequence to remove duplicates from.
    :return: The sequence with duplicates removed.
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def run():
    """
    Run the router service.
    """
    vehicle_ids = fetch_vehicle_ids()
    random_vehicle_id = random.choice(vehicle_ids)
    coordinates = fetch_coordinates(random_vehicle_id)
    region_graph = init_osmnx("Eindhoven, Noord-Brabant, Netherlands")
    route = map_to_map(region_graph, coordinates)
    # TODO: Do something with route, move logic to a route_calculator script, get routes from rabbitmq, get vehicle
    #  id's from vehicle service, add pricing, deal with double types Write the route object to a file after dumping
    #  to json
    with open("route.json", mode="w") as file:
        file.write(route.json())


if __name__ == "__main__":
    """
    Run the service.
    """
    run()
