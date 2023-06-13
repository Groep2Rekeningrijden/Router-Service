"""
Handler for route messages.
"""
import logging
import os
from time import sleep

import requests.exceptions
import src.router_service.services.data_fetcher as data_fetcher
from src.router_service.helpers.helpers import remove_way_id_lists
from src.router_service.models.vehicle import VehicleInt
from src.router_service.services.calculator import Calculator
from src.router_service.services.pricer import Pricer


class RouteHandler:
    """
    Handler for route messages.
    """

    def __init__(self):
        self.PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL")
        self.CAR_SERVICE_URL = os.environ.get("CAR_SERVICE_URL")

        self.calculator = Calculator()
        tries = 0
        try:
            price_model = data_fetcher.get_prices(self.PAYMENT_SERVICE_URL)
            self.pricer = Pricer(price_model=price_model)
            logging.warning("Got prices from payment service...")
        except requests.exceptions.ConnectionError as e:
            tries += 1
            if tries > 10:
                raise e
            sleep(5)

    def handle(self, publish_coordinates_dto):
        """
        Process the received message.

        :param publish_coordinates_dto:
        :return:
        """
        # --Input--
        # {
        # "vehicleId":"250aae3e-4c20-46e4-b5dc-7b32af4dbf9a",
        # "cords":[
        #   {"lat":1,"long":20,"timeStamp":"2023-06-01T13:04:30.4366085Z"},
        #   {"lat":3,"long":21,"timeStamp":"2023-06-01T13:04:30.4366608Z"}
        #   ]
        # }
        # Determine if request comes from international or domestic
        if "vehicle" in publish_coordinates_dto.keys():
            vehicle = VehicleInt.parse_obj(publish_coordinates_dto["vehicle"])
            coords = publish_coordinates_dto["points"]
            longitude_field = "lon"
            time_field = "time"
        else:
            vehicle = data_fetcher.get_vehicle(
                self.CAR_SERVICE_URL, publish_coordinates_dto["vehicleId"]
            )
            coords = publish_coordinates_dto["cords"]
            longitude_field = "long"
            time_field = "timeStamp"

        logging.warning(f"Received request for: {vehicle.id}")
        route = self.calculator.map_to_map(coordinates=coords, longitude_field=longitude_field, time_field=time_field)
        logging.warning(f"Processing price for: {vehicle.id}")
        route = self.pricer.calculate_price(route=route, vehicle=vehicle)
        # Workaround to deal with way lists. If anyone notices find a better fix :/
        route = remove_way_id_lists(route)
        return route
