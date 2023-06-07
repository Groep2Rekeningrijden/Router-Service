"""
Contains helper functions for the router service.
"""
import uuid

import pandas
from src.router_service.helpers.time import get_halfway_time
from src.router_service.models.route_models import Node, Route, Segment, Way


def remove_duplicates(seq):
    """
    Return a list with unique elements in the order they appear in the sequence.

    :param seq: The sequence to remove duplicates from.
    :return: The sequence with duplicates removed.
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def get_first_occurrence_indexes(seq):
    """
    Get a list of indexes for the first time every value appeared in the given list.

    :param seq: The sequence to get the indexes for.
    :return: A list of indexes for the first time every value appeared in the given list.
    """
    seen = set()
    seen_add = seen.add
    indexes = []
    for index, x in enumerate(seq):
        if x not in seen:
            indexes.append(index)
            seen_add(x)
    return indexes


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


def remove_way_id_lists(route: Route):
    """
    Remove the list of osmid's from the way object in each segment.

    This is done because the way object as agreed with other teams has a single way id.

    :param route: The route with segments that way id list have to be removed from.
    :return: The route with the lists replaced with their first element.
    """
    for seg in route.segments:
        if type(seg.way.osmid) is list:
            seg.way.osmid = seg.way.osmid[0]
    return route
