import networkx
import osmnx
import pandas
from geopandas import GeoDataFrame
from networkx import MultiDiGraph
from osmnx import settings, projection

from src.router_service.helpers import custom_nearest_edge as cne
from src.router_service.helpers.helpers import remove_duplicates, generate_formatted_route, get_first_occurrence_index
from src.router_service.models.route_models import Route


def get_start_and_end_time_of_edges(coordinates: list, nearest_edges: list) -> list[(str, str)]:
    first_occurrence_index = get_first_occurrence_index(nearest_edges)
    last_occurrence_index = get_first_occurrence_index(nearest_edges[::-1])
    # Get the first timestamp
    first_occurrence_timestamps = [[coordinate["timeStamp"] for coordinate in coordinates][i]
                                   for i in first_occurrence_index]
    last_occurrence_timestamps = [[coordinate["timeStamp"] for coordinate in coordinates][i]
                                  for i in last_occurrence_index]
    # No idea why but the timestamps where the wrong way around. Now they feel like they should be wrong but aren't...
    return [(x, y) for x, y in zip(last_occurrence_timestamps, first_occurrence_timestamps)]


def match_timestamps(nearest_edges: list[(int, int, int)], route_edges: GeoDataFrame,
                     edge_start_end_timestamps: list[(str, str)]):
    working_copy = route_edges.copy().reset_index()
    return_timestamps = {}
    for i, edge in working_copy.iterrows():
        try:
            index = nearest_edges.index((edge["u"], edge["v"], edge["key"]))
            return_timestamps[i] = edge_start_end_timestamps[index]
        except ValueError:
            continue
    return return_timestamps


def fill_timestamps(indexed_edge_timestamps: dict[int: tuple[str, str]], highest_index: int):
    """
    Fill in the missing indexes using neighbouring timestamps.
    """
    if 0 not in indexed_edge_timestamps.keys():
        propagate_nearest_timestamp(indexed_edge_timestamps, 0)
    if highest_index not in indexed_edge_timestamps.keys():
        propagate_nearest_timestamp(indexed_edge_timestamps, highest_index, upwards=False)
    for i in range(highest_index):
        if i not in indexed_edge_timestamps.keys():
            indexed_edge_timestamps = propagate_nearest_timestamp(indexed_edge_timestamps, i)
            indexed_edge_timestamps[i] = (indexed_edge_timestamps[i - 1][1], indexed_edge_timestamps[i + 1][0])
    return indexed_edge_timestamps


def propagate_nearest_timestamp(indexed_edge_timestamps, index, upwards=True):

    if upwards:
        stop = len(indexed_edge_timestamps)
        start = index + 1
        mod = 1
    else:
        stop = 0
        start = index
        mod = -1
    if start in indexed_edge_timestamps:
        return indexed_edge_timestamps

    for forward_index in range(start, stop):
        if forward_index + mod in indexed_edge_timestamps:
            indexed_edge_timestamps[forward_index] = indexed_edge_timestamps[forward_index + mod]
            for backward_index in range(forward_index, start, mod):
                indexed_edge_timestamps[backward_index - mod] = indexed_edge_timestamps[backward_index]
            return indexed_edge_timestamps
    return indexed_edge_timestamps


class Calculator:

    def __init__(self, region: str):
        self.area_graph = self.init_osmnx(region)
        self.geom, self.rtree = cne.init_rtree(self.area_graph)

    @staticmethod
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

    def fill_edge_gaps(self, nearest_edges: list) -> list:
        """
        Fill in the gaps between the nearest edges by adding all connected edges.

        :param nearest_edges: The edges that are the nearest to the given coordinates
        :return:
        """
        extra_edges = []
        for edge in nearest_edges:
            extra_edges.append(list(self.area_graph.in_edges(edge[0])))
            extra_edges.append(list(self.area_graph.out_edges(edge[0])))
            extra_edges.append(list(self.area_graph.in_edges(edge[1])))
            extra_edges.append(list(self.area_graph.out_edges(edge[1])))
        extra_edges = [item for sublist in extra_edges for item in sublist]
        extra_edges = [(edge[0], edge[1], 0) for edge in extra_edges]
        extra_edges = remove_duplicates(extra_edges)
        return extra_edges

    def get_sorted_route_df(self,
                            route_node_ids: list
                            ) -> (pandas.DataFrame, pandas.DataFrame):
        """
        Generate the route edges and nodes tables.

        Edges are sorted in the order their nodes appear in route.
        Nodes are not sorted.

        :param route_node_ids: The route to be mapped in the form of an ordered list of nodes.
        :return: The route edges and nodes tables.
        """
        route_nodes, route_edges = osmnx.graph_to_gdfs(self.area_graph.subgraph(route_node_ids))
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

    def map_to_map(self, coordinates: list) -> Route:
        """
        Map the given coordinates to the given map.

        :param coordinates: The coordinates to map
        :return:
        """
        # Get a list of edges that are the nearest to the given coordinates
        nearest_edges = [
            cne.nearest_edges(self.geom, self.rtree, coordinate["lat"], coordinate["long"])
            for coordinate in coordinates
        ]
        edge_start_end_timestamps = get_start_and_end_time_of_edges(coordinates, nearest_edges)
        nearest_edges = remove_duplicates(nearest_edges)

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
        extra_edges = self.fill_edge_gaps(nearest_edges)

        # Find the shortest route between the start and end using the filled graph
        route_node_ids = networkx.shortest_path(
            self.area_graph.edge_subgraph(nearest_edges + extra_edges),
            start,
            end,
        )

        # Get the route edges and nodes tables
        route_edges, route_nodes = self.get_sorted_route_df(route_node_ids)

        indexed_edge_timestamps = match_timestamps(nearest_edges, route_edges, edge_start_end_timestamps)
        indexed_edge_timestamps = fill_timestamps(indexed_edge_timestamps, len(route_edges.index))

        # Create the route object from the tables
        return generate_formatted_route(route_node_ids, route_edges, route_nodes, indexed_edge_timestamps)
