"""
Time helpers.
"""
import json
from datetime import datetime

from geopandas import GeoDataFrame
from src.router_service.helpers.helpers import get_first_occurrence_indexes


def get_start_and_end_time_of_edges(
    coordinates: list, nearest_edges: list, time_field: str
) -> list[(str, str)]:
    """
    Get the first and last timestamp associated with an edge.

    :param time_field:
    :param coordinates: coordinates list with timeStamp property
    :param nearest_edges: the edges to match timestamps to
    :return: the timestamps in the same order the edges are in
    """
    first_occurrence_index = get_first_occurrence_indexes(nearest_edges)
    last_occurrence_index = get_first_occurrence_indexes(nearest_edges[::-1])
    # Get the first timestamp
    first_occurrence_timestamps = [
        [coordinate[time_field] for coordinate in coordinates][i]
        for i in first_occurrence_index
    ]
    last_occurrence_timestamps = [
        [coordinate[time_field] for coordinate in coordinates][i]
        for i in last_occurrence_index
    ]
    # No idea why but the timestamps where the wrong way around. Now they feel like they should be wrong but aren't...
    return [
        (x, y) for x, y in zip(last_occurrence_timestamps, first_occurrence_timestamps)
    ]


def match_timestamps(
    nearest_edges: list[(int, int, int)],
    route_edges: GeoDataFrame,
    edge_start_end_timestamps: list[(str, str)],
):
    """
    Match the timestamps to the nearest edges they belong to.

    :param nearest_edges: The edges to match index with
    :param route_edges: The edges dataframe from which to get u/v/key
    :param edge_start_end_timestamps: The timestamps
    :return: The times with the same index as the matching edges.
    """
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

    :param edge_timestamps: The list of matched timestamps with indexes for their edge
    :param highest_index: The highest index to fill up to
    :return: edge_timestamps with missing indexes filled
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
            try:
                edge_timestamps[missing_range[0]] = edge_timestamps[min(missing_range) - 1]
                edge_timestamps[missing_range[-1]] = edge_timestamps[max(missing_range) + 1]
                missing_range.pop(0)
                missing_range.pop(-1)
            except KeyError as e:
                print(e)
                print("------------------------------")
                print("For ranges:")
                print(json.dumps(missing_ranges))
                print("------------------------------")
                print("For range:")
                print(json.dumps(missing_range))
                raise e
        # Do the 2 way copy for len 1 ranges
        if len(missing_range) == 1:
            edge_timestamps[missing_range[0]] = (
                edge_timestamps[missing_range[0] - 1][1],
                edge_timestamps[missing_range[0] + 1][0],
            )
        # This should only leave len 0  ranges, which we can move on from

    return edge_timestamps


def get_halfway_time(time_one, time_two):
    """
    Get the timestamp halfway between the start and end time.

    Requires string times with format "%Y-%m-%dT%H:%M:%S.%fZ".

    :param time_one: The first timestamp
    :param time_two: The second timestamp
    :return: The timestamp halfway between the two inputs
    """
    # Parse the datetime strings into datetime objects
    # TODO: This format doesn't match 2023-06-06T21:17:01.042Z
    start_time = datetime.fromisoformat(time_one)
    end_time = datetime.fromisoformat(time_two)

    # Calculate the time duration between the two datetime objects
    duration = end_time - start_time

    # Calculate the halfway time by adding half of the duration to the start time
    halfway_time = start_time + (duration / 2)

    # Convert the halfway time to a string
    halfway_time_str = halfway_time.strftime("%Y-%m-%d %H:%M:%S")

    return halfway_time_str
