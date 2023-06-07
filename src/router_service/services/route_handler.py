import logging
import os

import src.router_service.services.data_fetcher as data_fetcher
from src.router_service.helpers.helpers import remove_way_id_lists
from src.router_service.services.calculator import Calculator
from src.router_service.services.pricer import Pricer


class RouteHandler:
    def __init__(self):
        self.PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL")
        self.CAR_SERVICE_URL = os.environ.get("CAR_SERVICE_URL")

        self.calculator = Calculator()
        self.pricer = Pricer(price_model=data_fetcher.get_prices(self.PAYMENT_SERVICE_URL))

    def handle(self, publish_coordinates_dto):
        # --Input--
        # {
        # "VehicleId":"250aae3e-4c20-46e4-b5dc-7b32af4dbf9a",
        # "Cords":[
        #   {"Lat":1,"Long":20,"TimeStamp":"2023-06-01T13:04:30.4366085Z"},
        #   {"Lat":3,"Long":21,"TimeStamp":"2023-06-01T13:04:30.4366608Z"}
        #   ]
        # }
        logging.warning(f"Received request for: {publish_coordinates_dto['vehicleId']}")
        route = self.calculator.map_to_map(publish_coordinates_dto["cords"])
        logging.warning(f"Processing price for: {publish_coordinates_dto['vehicleId']}")
        route = self.pricer.calculate_price(route, data_fetcher.get_vehicle(self.CAR_SERVICE_URL,
                                                                            publish_coordinates_dto["vehicleId"]))
        # Workaround to deal with way lists. If anyone notices find a better fix :/
        route = remove_way_id_lists(route)
        return route
