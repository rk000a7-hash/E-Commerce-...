from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from database import db
from models.order import OrderModel, OrderCreate, OrderItem
from auth.dependencies import get_current_user, get_current_admin
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("/", response_model=OrderModel)
async def create_order(order_input: OrderCreate, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    
    # 1. Get User's Cart
    cart = await db.carts.find_one({"user_id": user_id})
    if not cart or not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # 2. Prepare Order Items and Recalculate Total
    order_items = []
    total_amount = 0.0
    
    for item in cart["items"]:
        product = await db.products.find_one({"_id": ObjectId(item["product_id"])})
        if not product:
            continue
            
        if product["stock"] < item["quantity"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough stock for product: {product['title']}"
            )
            
        order_items.append(OrderItem(
            product_id=str(product["_id"]),
            title=product["title"],
            price=product["price"],
            quantity=item["quantity"],
            image=product["image"]
        ))
        total_amount += product["price"] * item["quantity"]
        
        # 3. Decrease stock
        await db.products.update_one(
            {"_id": product["_id"]},
            {"$inc": {"stock": -item["quantity"]}}
        )

    # 4. Create Order Object
    new_order = {
        "user_id": user_id,
        "user_email": current_user["email"],
        "items": [item.model_dump() for item in order_items],
        "total_amount": total_amount,
        "shipping_address": order_input.shipping_address.model_dump(),
        "status": "Pending",
        "created_at": datetime.utcnow()
    }
    
    result = await db.orders.insert_one(new_order)
    
    # 5. Clear User's Cart
    await db.carts.update_one(
        {"user_id": user_id},
        {"$set": {"items": [], "total_price": 0.0, "updated_at": datetime.utcnow()}}
    )
    
    created_order = await db.orders.find_one({"_id": result.inserted_id})
    created_order["id"] = created_order["_id"]
    return created_order

@router.get("/me", response_model=List[OrderModel])
async def get_my_orders(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    orders = await db.orders.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    for order in orders:
        order["id"] = order["_id"]
    return orders

@router.get("/", response_model=List[OrderModel])
async def get_all_orders(current_admin: dict = Depends(get_current_admin)):
    orders = await db.orders.find().sort("created_at", -1).to_list(100)
    for order in orders:
        order["id"] = order["_id"]
    return orders

@router.put("/{order_id}/status")
async def update_order_status(order_id: str, status: str, current_admin: dict = Depends(get_current_admin)):
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
        
    result = await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": status}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
        
    return {"message": "Order status updated successfully"}
