"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel
from typing import List, Optional


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total: float
    items: Optional[List[OrderItemResponse]] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    price: str
    sku: str
    stock: int


class UserOrderResponse(BaseModel):
    id: int
    status: str
    total: float
