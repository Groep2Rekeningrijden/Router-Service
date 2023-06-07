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


def fill_timestamps(edge_timestamps: dict[int: tuple[str, str]], highest_index: int):
    """
    Fill in the missing indexes using neighbouring timestamps.
    """
    missing_ranges = []
    # Find ranges of missing indexes
    for i in range(highest_index):
        if i in edge_timestamps.keys():
            continue
        if len(missing_ranges) == 0:
            missing_ranges.append([i])
        elif missing_ranges[-1][-1] == i - 1:
            missing_ranges[-1].append(i)
        else:
            missing_ranges.append([i])

    # First, make sure index 0 and highest_index have timestamps
    # by setting all elements in that list to the first/last element that has a timestamp
    if 0 in missing_ranges[0]:
        for i in missing_ranges[0]:
            edge_timestamps[i] = edge_timestamps[max(missing_ranges[0]) + 1]
        missing_ranges.pop(0)
    if highest_index in missing_ranges[-1]:
        for i in missing_ranges[-1]:
            edge_timestamps[i] = edge_timestamps[min(missing_ranges[-1]) - 1]
        missing_ranges.pop(-1)

    for index, missing_range in enumerate(missing_ranges):
        # For longer ranges, full copy both sides, then check if any elements are left empty
        while len(missing_range) > 1:
            edge_timestamps[missing_range[0]] = edge_timestamps[min(missing_range) - 1]
            missing_range.pop(0)
            edge_timestamps[missing_range[-1]] = edge_timestamps[max(missing_range) + 1]
            missing_range.pop(-1)
        # Do the 2 way copy for len 1 ranges
        if len(missing_range) == 1:
            edge_timestamps[missing_range[0]] = (
                edge_timestamps[missing_range[0] - 1][1], edge_timestamps[missing_range[0] + 1][0])
        # This should only leave len 0  ranges, which we can move on from

    return edge_timestamps
