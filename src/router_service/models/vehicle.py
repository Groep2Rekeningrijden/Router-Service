"""
The vehicle model.
"""
from pydantic import BaseModel


class Vehicle(BaseModel):
    """
    Pydantic vehicle model.
    """

    id: str
    licence: str
    classification: str
    fuelType: str
