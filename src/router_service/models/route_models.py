"""
Route models.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class Node(BaseModel):
    """
    Model for node.

    :param osmid: OSM ID
    :param lat: Latitude
    :param lon: Longitude
    """

    osmid: int = Field(alias="id")
    lat: float = Field(alias="lat")
    lon: float = Field(alias="lon")
    time: datetime = Field(exclude=True)


class Way(BaseModel):
    """
    Model for way.

    :param osmid: OSM ID
    :param name: The name of the road
    :param highway: The highway type based on OSM
    :param length: Length in meters
    """

    osmid: int | list[int] = Field(alias="id")
    name: str | list[str] = Field(exclude=True)
    highway: str | list[str] = Field(exclude=True)
    # TODO: Add boundary to the model
    # boundary: str | list[str]
    length: float = Field(exclude=True)


class Segment(BaseModel):
    """
    Model for segment.

    :param start: Start node
    :param way: Way
    :param end: End node
    :param time: Time of the segment
    :param price: Price of the segment
    """

    start: Node = Field(alias="start")
    way: Way = Field(alias="way")
    end: Node = Field(alias="end")
    time: datetime = Field(alias="time", default=None)
    price: float = Field(alias="price", default=0.0)


class Route(BaseModel):
    """
    Model for route.

    :param route_id: ID of the route
    :param price_total: Total price of the route
    :param segments: Segments of the route. Defaults to empty if not given
    """

    vehicle_id: uuid.UUID = Field(alias="id", default=None)
    price_total: float = Field(alias="priceTotal", default=0.0)
    segments: list[Segment] = Field(alias="segments", default=None)

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
