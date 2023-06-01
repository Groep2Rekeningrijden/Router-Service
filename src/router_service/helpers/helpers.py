import uuid

import pandas

from src.router_service.models.route_models import Route, Segment, Node, Way


def ordered_unique_list(seq):
    """
    Return a list with unique elements in the order they appear in the sequence.

    :param seq: The sequence to remove duplicates from.
    :return: The sequence with duplicates removed.
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def generate_formatted_route(route: list, route_edges: pandas.DataFrame, route_nodes: pandas.DataFrame
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
