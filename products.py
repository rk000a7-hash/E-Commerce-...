from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from database import db
from models.product import ProductModel, ProductCreate, ProductUpdate
from auth.dependencies import get_current_admin, get_current_user
from bson import ObjectId

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/", response_model=List[ProductModel])
async def get_products():
    products = await db.products.find().to_list(100)
    for p in products:
        p["id"] = p["_id"]
    return products

@router.get("/{id}", response_model=ProductModel)
async def get_product(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
        
    product = await db.products.find_one({"_id": ObjectId(id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    product["id"] = product["_id"]
    return product

@router.post("/", response_model=ProductModel)
async def create_product(product: ProductCreate, current_admin: dict = Depends(get_current_admin)):
    product_dict = product.model_dump()
    result = await db.products.insert_one(product_dict)
    
    new_product = await db.products.find_one({"_id": result.inserted_id})
    new_product["id"] = new_product["_id"]
    return new_product

@router.put("/{id}", response_model=ProductModel)
async def update_product(id: str, product_update: ProductUpdate, current_admin: dict = Depends(get_current_admin)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
        
    update_data = {k: v for k, v in product_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No updates provided")
        
    result = await db.products.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found or no changes made")
        
    updated_product = await db.products.find_one({"_id": ObjectId(id)})
    updated_product["id"] = updated_product["_id"]
    return updated_product

@router.delete("/{id}")
async def delete_product(id: str, current_admin: dict = Depends(get_current_admin)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
        
    result = await db.products.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return {"message": "Product deleted successfully"}
