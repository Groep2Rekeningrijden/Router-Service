import json
import logging

from geopandas import GeoDataFrame

from src.router_service.helpers.helpers import get_first_occurrence_index


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
    try:
        if 0 not in indexed_edge_timestamps.keys():
            propagate_nearest_timestamp(indexed_edge_timestamps, 0, highest_index)
        if highest_index not in indexed_edge_timestamps.keys():
            propagate_nearest_timestamp(indexed_edge_timestamps, highest_index, 0, upwards=False)
        for i in range(highest_index - 1):
            if i not in indexed_edge_timestamps.keys():
                indexed_edge_timestamps = propagate_nearest_timestamp(indexed_edge_timestamps, i, highest_index)
        return indexed_edge_timestamps
    except KeyError as e:
        logging.error(highest_index)
        logging.error(json.dumps(indexed_edge_timestamps))
        raise e


def propagate_nearest_timestamp(indexed_edge_timestamps, index, highest_index, upwards=True):
    if upwards:
        stop = highest_index
        start = index + 1
        mod = 1
    else:
        stop = 0
        start = index - 1
        mod = -1
    # If the next element has a timestamp
    if start in indexed_edge_timestamps:
        # Use it IF the current index is the first or last element, since those can't pull from both sides
        if index == 0 or index == highest_index - 1:
            indexed_edge_timestamps[index] = indexed_edge_timestamps[start]
            return indexed_edge_timestamps
        # Otherwise, combine from previous and next element
        indexed_edge_timestamps[index] = (indexed_edge_timestamps[index - 1][1], indexed_edge_timestamps[index + 1][0])
        return indexed_edge_timestamps

    # If the next element doesn't have a timestamp, find the next one that does, then propagate backwards
    for forward_index in range(start, stop, mod):
        if forward_index + mod in indexed_edge_timestamps:
            indexed_edge_timestamps[forward_index] = indexed_edge_timestamps[forward_index + mod]
            for backward_index in range(forward_index, index, - mod):
                indexed_edge_timestamps[backward_index - mod] = indexed_edge_timestamps[backward_index]
            return indexed_edge_timestamps
    return indexed_edge_timestamps
