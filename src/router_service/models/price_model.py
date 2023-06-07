"""
Models for pricing.
"""
from typing import List

from pydantic import BaseModel


class PriceModifier(BaseModel):
    """
    The pydantic model for a PriceModifier.
    """

    id: str
    priceTitle: str
    priceType: str
    valueName: str
    valueDescription: float


class PriceModel(BaseModel):
    """
    The pydantic model for a list of PriceModifiers.
    """

    __root__: List[PriceModifier]

    def __iter__(self):
        """
        Get the iterable list.

        :return: list
        """
        return iter(self.__root__)
