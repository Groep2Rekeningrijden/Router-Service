"""
Responsible for calculating segment prices.
"""
from src.router_service.models.price_model import PriceModel
from src.router_service.models.route_models import Node, Way, Segment, Route
from src.router_service.models.vehicle import Vehicle


class Pricer:
    def __init__(self, price_model: PriceModel):
        self.price_model = price_model

    def calculate_price(self, route: Route, vehicle: Vehicle):

        for segment in route.segments:
            # segment_price = base_road_price * distance * (road_type_modifier + region_modifier + vehicle_category * fuel_type)
            segment.price = 0


