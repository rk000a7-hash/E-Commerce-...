from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from utils.pyobjectid import PyObjectId

class CartItem(BaseModel):
    product_id: str
    quantity: int

    model_config = {
        "populate_by_name": True,
    }

class CartModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    items: List[CartItem] = []
    total_price: float = 0.0
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
    }

class CartAdd(BaseModel):
    product_id: str
    quantity: int

class CartUpdate(BaseModel):
    product_id: str
    quantity: int
