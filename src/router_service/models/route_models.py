import uuid
from datetime import datetime


class Node:
    # params: osmid, lat, lon
    def __init__(self, osmid, lat, lon):
        self.osmid = osmid
        self.lat = lat
        self.lon = lon


class Way:
    # params: osmid, name, highway, length, price
    def __init__(self, osmid, name, highway, length):
        self.osmid = osmid
        self.name = name
        self.highway = highway
        self.length = length
        self.price = None


class Segment:
    # Params: start, way, end
    def __init__(self, start: Node, way: Way, end: Node, time: datetime = None, price: float = 0):
        self.time = time
        self.price = price
        self.start = start
        self.way = way
        self.end = end


class Route:
    def __init__(self, id: uuid, price_total: float = 0, segments: list[Segment] = None):
        self.id = id
        self.price_total = price_total
        self.segments = segments

    def add_segment(self, segment: Segment):
        self.segments.append(segment)
        self.price_total += segment.price
