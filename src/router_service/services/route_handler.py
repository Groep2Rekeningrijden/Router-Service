import json
import logging

from src.router_service.models.route_models import RouteDTO
from src.router_service.services.calculator import Calculator


class RouteHandler:
    def __init__(self, region, price_model):
        self.calculator = Calculator(region=region)
        self.price_model = price_model

    def handle(self, publish_coordinates_dto):
        # --Input--
        # {
        # "VehicleId":"250aae3e-4c20-46e4-b5dc-7b32af4dbf9a",
        # "Cords":[
        #   {"Lat":1,"Long":20,"TimeStamp":"2023-06-01T13:04:30.4366085Z"},
        #   {"Lat":3,"Long":21,"TimeStamp":"2023-06-01T13:04:30.4366608Z"}
        #   ]
        # }
        route = RouteDTO(publish_coordinates_dto["VehicleId"],
                         self.calculator.map_to_map(publish_coordinates_dto["Cords"]))
        
        logging.warning(route.json())

        return route
