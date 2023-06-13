"""
Contains helper functions for the router service.
"""

from src.router_service.models.route_models import Route


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
