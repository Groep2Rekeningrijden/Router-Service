"""
Custom version of osmnx.distance.nearest_edges.
"""
import numpy as np
import pandas
from networkx import MultiDiGraph
from osmnx import utils_graph
from shapely import Point, STRtree


def init_rtree(graph: MultiDiGraph):
    """
    Initialize the geoms and rtree for use in nearest edges.

    We do this separately so we can reuse the objects for multiple routes.
    """
    geoms = utils_graph.graph_to_gdfs(graph, nodes=False)["geometry"]
    # build the r-tree spatial index by position for subsequent iloc
    rtree = STRtree(geoms)
    return geoms, rtree


def nearest_edges(
    geoms: pandas.DataFrame,
    rtree: STRtree,
    lats: list,
    lons: list,
):
    """
    Rewrite of the osmnx.distance.nearest_edges function to fit our use case.

    :param geoms: Dataframe containing the geometry of the map.
    :param rtree: A query-only R-tree spatial index created using the Sort-Tile-Recursive (STR) algorithm.
    :param lats: List of latitudes.
    :param lons: List of longitudes.
    """
    is_scalar = False
    if not (hasattr(lats, "__iter__") and hasattr(lons, "__iter__")):
        # make coordinates arrays if user passed non-iterable values
        is_scalar = True
        lats = np.array([lats])
        lons = np.array([lons])

    if np.isnan(lats).any() or np.isnan(lons).any():  # pragma: no cover
        raise ValueError("`X` and `Y` cannot contain nulls")

    # use r-tree to find each point's nearest neighbor and distance
    points = [Point(xy) for xy in zip(lats, lons)]
    pos = rtree.query_nearest(points, all_matches=False, return_distance=False)

    # if user passed X/Y lists, the 2nd subarray contains geom indices
    if len(pos.shape) > 1:
        pos = pos[1]
    ne = geoms.iloc[pos].index

    # convert results to correct types for return
    ne = list(ne)
    if is_scalar:
        ne = ne[0]

    return ne
