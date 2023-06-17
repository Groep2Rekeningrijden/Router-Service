import os
import pickle

import psutil
from src.router_service.helpers import custom_nearest_edge as cne
from Simulation.tracker_generator.tracker_generator.generator import init_osmnx


def generate_and_pickle():
    graph = init_osmnx("PLACE", os.environ.get("REGION"))
    geom, rtree = cne.init_rtree(graph)
    with open("graph.pickle", "wb") as f:
        pickle.dump(graph, f)
    with open("geom.pickle", "wb") as f:
        pickle.dump(geom, f)
    with open("rtree.pickle", "wb") as f:
        pickle.dump(rtree, f)


def estimate_memory_impact():
    # Get current memory usage
    memory_at_start = psutil.virtual_memory()[3] / 1_000_000
    # load the graph, geom and rtree pickles
    with open("graph.pickle", "rb") as f:
        graph = pickle.load(f)
    with open("geom.pickle", "rb") as f:
        geom = pickle.load(f)
    with open("rtree.pickle", "rb") as f:
        rtree = pickle.load(f)
    memory_at_end = psutil.virtual_memory()[3] / 1_000_000
    print(f"{memory_at_end - memory_at_start} MB memory used")
    # Get the columns of geom
    columns = list(graph.columns)
    print(columns)

