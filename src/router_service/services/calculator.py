import networkx
import osmnx
import pandas
from networkx import MultiDiGraph
from osmnx import settings, projection

from src.router_service.helpers import custom_nearest_edge as cne
from src.router_service.helpers.helpers import ordered_unique_list, generate_formatted_route
from src.router_service.models.route_models import Route


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
        extra_edges = self.fill_edge_gaps(nearest_edges)

        # Find the shortest route between the start and end using the filled graph
        route_node_ids = networkx.shortest_path(
            networkx.Graph.edge_subgraph(nearest_edges + extra_edges),
            start,
            end,
        )

        # Get the route edges and nodes tables
        route_edges, route_nodes = self.get_sorted_route_df(route_node_ids)

        # Create the route object from the tables
        return generate_formatted_route(route_node_ids, route_edges, route_nodes)

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
        extra_edges = ordered_unique_list(extra_edges)
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
