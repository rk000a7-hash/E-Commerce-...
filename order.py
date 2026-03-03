from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from utils.pyobjectid import PyObjectId

class OrderItem(BaseModel):
    product_id: str
    title: str
    price: float
    quantity: int
    image: str

class ShippingAddress(BaseModel):
    full_name: str
    address_line: str
    city: str
    state: str
    zip_code: str
    country: str

class OrderModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    user_email: str
    items: List[OrderItem]
    total_amount: float
    shipping_address: ShippingAddress
    status: str = "Pending"  # Pending, Processing, Shipped, Delivered, Cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
    }

class OrderCreate(BaseModel):
    shipping_address: ShippingAddress
