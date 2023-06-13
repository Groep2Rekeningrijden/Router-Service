"""
Responsible for calculating segment prices.
"""
from src.router_service.helpers.price_helpers import (
    get_price_mod_for,
    int_to_percent_increase_multiplier,
    to_int_percent,
)
from src.router_service.models.price_model import PriceModel
from src.router_service.models.route_models import Route
from src.router_service.models.vehicle import VehicleInt


class Pricer:
    """
    Price calculator.
    """

    def __init__(self, price_model: PriceModel):
        self.price_model = price_model
        self.base_road_price = 20  # in cents
        self.highway_lookup = {}
        self.boundary_lookup = {}
        self.vehicle_classification_lookup = {}
        self.fuel_type_lookup = {}
        self.rush_lookup = {}

        for price in price_model:
            match price.priceTitle:
                case "basePrice":
                    self.base_road_price = price.valueDescription * 100
                case "highway":
                    self.highway_lookup[price.valueName] = to_int_percent(
                        price.valueDescription
                    )
                case "boundary":
                    self.boundary_lookup[price.valueName] = to_int_percent(
                        price.valueDescription
                    )
                case "vehicleClassification":
                    self.vehicle_classification_lookup[
                        price.valueName
                    ] = to_int_percent(price.valueDescription)
                case "fuelType":
                    self.fuel_type_lookup[price.valueName] = to_int_percent(
                        price.valueDescription
                    )
                case "rushPrice":
                    self.rush_lookup[price.valueName] = to_int_percent(
                        price.valueDescription
                    )

    def calculate_price(self, route: Route, vehicle: VehicleInt):
        """
        Calculate the price of a route for the given vehicle.

        :param route: The route
        :param vehicle: The vehicle
        :return: The route with prices added
        """
        vehicle_classification_mod = get_price_mod_for(
            [vehicle.vehicleClassification], self.vehicle_classification_lookup
        )
        fuel_type_mod = get_price_mod_for([vehicle.fuelType], self.fuel_type_lookup)

        """
        segment_price =
            base_road_price (set to something)
            * distance (length of way)
            * ( highway lookup way.highway in {type: price_mod}
                + boundary lookup way.boundary in  {type: price_mod}
                + vehicleClassification lookup Vehicle.classification in {type: price_mod}
                + fuelType lookup Vehicle.fuelType in {type: price_mod}
                + rushPrice lookup way.time.hour in {hour: price_per_km})
        """
        for segment in route.segments:
            distance = segment.way.length
            highway_mod = get_price_mod_for(segment.way.highway, self.highway_lookup)
            # TODO: boundary_mod = get_price_mod_for(segment.way.boundary, self.boundary_lookup)
            rush_hour_mod = self.rush_lookup.get(str(segment.time.hour), 0)
            total_mod = int_to_percent_increase_multiplier(
                highway_mod + vehicle_classification_mod + fuel_type_mod + rush_hour_mod
            )
            # Calculations use cents, end result want euro's
            segment.price = (
                round(self.base_road_price * distance * (total_mod + 1), 2) / 100
            )

        route.price_total = round(sum([segment.price for segment in route.segments]), 2)
        route.vehicle_id = vehicle.id
        return route
