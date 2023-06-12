"""
Handler for route messages.
"""
import logging
import os
from time import sleep

import requests.exceptions

import src.router_service.services.data_fetcher as data_fetcher
from src.router_service.helpers.helpers import remove_way_id_lists
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
            self.pricer = Pricer(
                price_model=price_model
            )
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
        logging.warning(f"Received request for: {publish_coordinates_dto['vehicleId']}")
        route = self.calculator.map_to_map(publish_coordinates_dto["cords"])
        logging.warning(f"Processing price for: {publish_coordinates_dto['vehicleId']}")
        route = self.pricer.calculate_price(
            route,
            data_fetcher.get_vehicle(
                self.CAR_SERVICE_URL, publish_coordinates_dto["vehicleId"]
            ),
        )
        # Workaround to deal with way lists. If anyone notices find a better fix :/
        route = remove_way_id_lists(route)
        return route
