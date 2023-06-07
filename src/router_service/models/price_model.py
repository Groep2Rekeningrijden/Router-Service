from typing import List

from pydantic import BaseModel


class PriceModifier(BaseModel):
    id: str
    priceTitle: str
    priceType: str
    valueName: str
    valueDescription: float


class PriceModel(BaseModel):
    __root__: List[PriceModifier]

    def __iter__(self):
        return iter(self.__root__)