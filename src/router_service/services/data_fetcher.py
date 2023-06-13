"""
Handles API requests for fetching data.
"""
import logging

import requests
from src.router_service.models.price_model import PriceModel
from src.router_service.models.vehicle import Vehicle, VehicleInt


def get_prices(payment_service_url) -> PriceModel:
    """
    Get the price model from the payment service.

    :return: Price model
    """
    try:
        response = requests.get(payment_service_url)
        response.raise_for_status()
        price_model = PriceModel.parse_obj(response.json())
    except requests.exceptions.RequestException as e:
        logging.error("Could not get price model from payment service.")
        raise e
    return price_model


def get_vehicle(car_service_url, vehicle_id) -> VehicleInt:
    """
    Get the vehicle from the car service.

    :param car_service_url: Car service url
    :param vehicle_id: Vehicle id
    :return: Vehicle model
    """
    try:
        response = requests.get(car_service_url, params={"vehicleId": vehicle_id})
        response.raise_for_status()
        vehicle = Vehicle.parse_obj(response.json())
        vehicle = VehicleInt(
            id=vehicle.id,
            vehicleClassification=vehicle.vehicleClassification,
            fuelType=vehicle.fuelType,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Could not get vehicle with id {vehicle_id} from car service.")
        raise e
    return vehicle
