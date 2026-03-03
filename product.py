from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from utils.pyobjectid import PyObjectId

class ProductModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: str
    price: float
    image: str
    category: str
    stock: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "title": "Smartphone",
                "description": "Latest model smartphone",
                "price": 599.99,
                "image": "url_to_image",
                "category": "Electronics",
                "stock": 50
            }
        }
    }

class ProductCreate(BaseModel):
    title: str
    description: str
    price: float
    image: str
    category: str
    stock: int

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    category: Optional[str] = None
    stock: Optional[int] = None
