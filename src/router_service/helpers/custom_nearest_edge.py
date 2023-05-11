import numpy as np
from osmnx import utils_graph
from shapely import STRtree, Point

def init_rtree(graph):
    geoms = utils_graph.graph_to_gdfs(graph, nodes=False)["geometry"]
    # build the r-tree spatial index by position for subsequent iloc
    rtree = STRtree(geoms)
    return geoms, rtree

def nearest_edges(geoms, rtree, X, Y, ):
    """

    """
    is_scalar = False
    if not (hasattr(X, "__iter__") and hasattr(Y, "__iter__")):
        # make coordinates arrays if user passed non-iterable values
        is_scalar = True
        X = np.array([X])
        Y = np.array([Y])

    if np.isnan(X).any() or np.isnan(Y).any():  # pragma: no cover
        raise ValueError("`X` and `Y` cannot contain nulls")

    # use r-tree to find each point's nearest neighbor and distance
    points = [Point(xy) for xy in zip(X, Y)]
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