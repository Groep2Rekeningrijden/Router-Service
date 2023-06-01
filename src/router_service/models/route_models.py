"""
Route models.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel


class Node(BaseModel):
    """
    Model for node.

    :param osmid: OSM ID
    :param lat: Latitude
    :param lon: Longitude
    """

    osmid: int
    lat: float
    lon: float


class Way(BaseModel):
    """
    Model for way.

    :param osmid: OSM ID
    :param name: The name of the road
    :param highway: The highway type based on OSM
    :param length: Length in meters
    """

    osmid: int | list[int]
    name: str | list[str]
    highway: str | list[str]
    length: float
    price: float = None


class Segment(BaseModel):
    """
    Model for segment.

    :param start: Start node
    :param way: Way
    :param end: End node
    :param time: Time of the segment
    :param price: Price of the segment
    """

    start: Node
    way: Way
    end: Node
    time: datetime = None
    price: float = 0


class Route(BaseModel):
    """
    Model for route.

    :param route_id: ID of the route
    :param price_total: Total price of the route
    :param segments: Segments of the route. Defaults to empty if not given
    """

    route_id: uuid.UUID = uuid.uuid4()
    price_total: float = 0
    segments: list[Segment] = None

    def __init__(self, *args, **kwargs):
        """
        Initialize the route.
        """
        super().__init__(*args, **kwargs)
        if not self.segments:
            self.segments = []

    def add_segment(self, segment: Segment):
        """
        Add a segment to the route.

        :param segment: Segment to add.
        :return: None.
        """
        self.segments.append(segment)


class RouteDTO(BaseModel):
    """
    Model for transmitting route.

    :param VehicleId: ID of the vehicle
    :param Route: The Route object
    """
    VehicleId: uuid.UUID
    Route: Route
