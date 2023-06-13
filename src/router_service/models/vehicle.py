"""
The vehicle model.
"""
from pydantic import BaseModel


class VehicleInt(BaseModel):
    """
    Pydantic vehicle model as agreed with international teams.
    """

    id: str
    vehicleClassification: str
    fuelType: str


class Vehicle(VehicleInt):
    """
    Pydantic vehicle model.
    """

    licence: str
