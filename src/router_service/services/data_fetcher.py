"""
    Handles API requests for fetching data.
    """
import json
import logging

import requests

from src.router_service.models.price_model import PriceModel
from src.router_service.models.vehicle import Vehicle


def get_prices() -> PriceModel:
    """
    Gets the price model from the payment service.
    :return: Price model
    """
    try:
        # response = requests.get('https://payment-service/getPrices')
        response = requests.get('http://localhost:5051/getPrices')
        response.raise_for_status()
        price_model = PriceModel.parse_obj(response.json())
    except requests.exceptions.RequestException as e:
        logging.error('Could not get price model from payment service.')
        raise e
    return price_model


def get_vehicle(vehicle_id) -> Vehicle:
    """
    Gets the vehicle from the car service.
    :param vehicle_id: Vehicle id
    :return: Vehicle model
    """
    try:
        # response = requests.get(f'https://car-service/vehicle?vehicleId={vehicle_id}')
        response = requests.get(f'https://localhost:5055/vehicle?vehicleId={vehicle_id}')
        response.raise_for_status()
        vehicle = Vehicle.parse_obj(response.json())
    except requests.exceptions.RequestException as e:
        logging.error(f'Could not get vehicle with id {vehicle_id} from car service.')
        raise e
    return vehicle
