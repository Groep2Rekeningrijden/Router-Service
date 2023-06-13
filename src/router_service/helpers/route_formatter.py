"""
Contains the RouteFormatter for formatting routes into a Route model.
"""
import uuid

import pandas
from src.router_service.helpers.time import get_halfway_time
from src.router_service.models.route_models import Node, Route, Segment, Way


def generate_formatted_route(
    route: list,
    route_edges: pandas.DataFrame,
    route_nodes: pandas.DataFrame,
    indexed_edge_timestamps: dict[int : tuple[str, str]],
) -> Route:
    """
    Generate a route using the Route model as specified in the route_models.

    :param route: List of ordered nodes in the route.
    :param route_edges: Dataframe containing the edges of the route in order.
    :param route_nodes: Dataframe containing the nodes of the route.
    :param indexed_edge_timestamps: Timestamps with same index as the edge they belong to.
    :return: The route as a Route model.

    """
    out = Route(route_id=uuid.uuid4())
    for index, node in enumerate(route[:-2]):
        next_node = route[index + 1]
        start_data = route_nodes.loc[node, ["lon", "lat"]].to_dict()
        end_data = route_nodes.loc[next_node, ["lon", "lat"]].to_dict()
        way_data = route_edges.iloc[index].fillna("").to_dict()
        start, end = indexed_edge_timestamps[index]

        out.add_segment(
            Segment(
                start=Node(
                    id=node, lon=start_data["lon"], lat=start_data["lat"], time=start
                ),
                way=Way(
                    id=way_data["osmid"],
                    name=way_data["name"],
                    highway=way_data["highway"],
                    length=way_data["length"] / 1000,
                ),
                end=Node(
                    id=next_node, lon=end_data["lon"], lat=end_data["lat"], time=end
                ),
                time=get_halfway_time(start, end),
            )
        )
    return out
