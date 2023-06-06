import uuid
from datetime import datetime

import pandas

from src.router_service.models.route_models import Route, Segment, Node, Way


def get_halfway_time(start_time_str, end_time_str):
    # Parse the datetime strings into datetime objects
    # TODO: This format doesn't match 2023-06-06T21:17:01.042Z
    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

    # Calculate the time duration between the two datetime objects
    duration = end_time - start_time

    # Calculate the halfway time by adding half of the duration to the start time
    halfway_time = start_time + (duration / 2)

    # Convert the halfway time to a string
    halfway_time_str = halfway_time.strftime('%Y-%m-%d %H:%M:%S')

    return halfway_time_str


def remove_duplicates(seq):
    """
    Return a list with unique elements in the order they appear in the sequence.

    :param seq: The sequence to remove duplicates from.
    :return: The sequence with duplicates removed.
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def get_first_occurrence_index(seq):
    seen = set()
    seen_add = seen.add
    indexes = []
    for index, x in enumerate(seq):
        if x not in seen:
            indexes.append(index)
            seen_add(x)
    return indexes


def generate_formatted_route(route: list, route_edges: pandas.DataFrame, route_nodes: pandas.DataFrame,
                             indexed_edge_timestamps: dict[int: tuple[str, str]]
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
        start, end = indexed_edge_timestamps[index]

        out.add_segment(
            Segment(
                start=Node(osmid=node, lon=start_data["lon"], lat=start_data["lat"], time=start),
                way=Way(
                    osmid=way_data["osmid"],
                    name=way_data["name"],
                    highway=way_data["highway"],
                    length=way_data["length"],
                    time=get_halfway_time(start, end)
                ),
                end=Node(osmid=next_node, lon=end_data["lon"], lat=end_data["lat"], time=end),
            )
        )
    return out
