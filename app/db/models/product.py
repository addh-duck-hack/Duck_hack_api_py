from pydantic import BaseModel
from typing import Optional

class Product_characteristic(BaseModel):
    name: str
    value: str

class Product_characteristics(BaseModel):
    name: str
    characteristic: list[Product_characteristic]

class Product_image(BaseModel):
    id: str
    sku: str
    name: str
    alt: str
    url: str

class Product(BaseModel):
    id: str
    sku: str
    name: str
    original_price: float
    discount: float
    final_price: float
    offer: str
    start_offer: str
    end_offer: str
    shipping_cost: float
    stock: int
    description: str
    characteristics: list[Product_characteristics]
    delivery_terms: str
    images: list[Product_image]
    registration_date: str
    disabled: bool




