from pydantic import BaseModel


class Vehicle(BaseModel):
    id: str
    licence: str
    classification: str
    fuelType: str
