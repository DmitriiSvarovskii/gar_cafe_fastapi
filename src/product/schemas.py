from datetime import datetime
from pydantic import BaseModel
from typing import List


class ProductList(BaseModel):
    id: int
    shop_id: int
    category_id: int
    name_rus: str = None
    # name_en: str = None
    description_rus: str = None
    # description_en: str = None
    price: float = None
    image: str
    availability: bool = True
    popular: bool = False
    type_delivery: bool = True
    type_takeaway: bool = True
    type_inside: bool = True


class ProductOne(ProductList):
    shop_id: int
    category_id: int
    name_rus: str = None
    name_en: str = None
    description_rus: str = None
    description_en: str = None
    price: float = None
    image: str
    wt: int = None
    unit: int
    kilocalories: int = None
    proteins: int = None
    fats: int = None
    carbohydrates: int = None
    availability: bool = True
    popular: bool = False
    type_delivery: bool = True
    type_takeaway: bool = True
    type_inside: bool = True


class ProductCreate(ProductOne):
    pass


class ProductUpdate(ProductOne):
    pass


class ProductModel(ProductOne):
    id: int
    # created_at: datetime

    class Config:
        orm_mode = True


class UnitBase(BaseModel):
    name: str


class UnitCreate(UnitBase):
    pass


class UnitUpdate(UnitBase):
    pass


class UnitModel(UnitBase):
    id: int

    class Config:
        orm_mode = True

    class Config:
        orm_mode = True
