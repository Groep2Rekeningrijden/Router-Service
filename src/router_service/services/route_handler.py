import logging
import src.router_service.services.data_fetcher as data_fetcher

from src.router_service.services.calculator import Calculator
from src.router_service.services.pricer import Pricer


class RouteHandler:
    def __init__(self, region):
        self.calculator = Calculator(region=region)
        self.pricer = Pricer(price_model=data_fetcher.get_prices())

    def handle(self, publish_coordinates_dto):
        # --Input--
        # {
        # "VehicleId":"250aae3e-4c20-46e4-b5dc-7b32af4dbf9a",
        # "Cords":[
        #   {"Lat":1,"Long":20,"TimeStamp":"2023-06-01T13:04:30.4366085Z"},
        #   {"Lat":3,"Long":21,"TimeStamp":"2023-06-01T13:04:30.4366608Z"}
        #   ]
        # }
        route = self.calculator.map_to_map(publish_coordinates_dto["cords"])
        route = self.pricer.calculate_price(route, data_fetcher.get_vehicle(publish_coordinates_dto["vehicleId"]))

        logging.warning(route.json())

        return route
