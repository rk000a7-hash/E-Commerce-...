from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.responses import JSONResponse
from database import db
from auth.dependencies import get_current_user
from bson import ObjectId
from datetime import datetime
import json

router = APIRouter(prefix="/api/cart", tags=["cart"])

def serialise_cart(cart):
    if not cart: return None
    cart["id"] = str(cart.get("_id", ""))
    if "_id" in cart: del cart["_id"]
    if "user_id" in cart: cart["user_id"] = str(cart["user_id"])
    if "updated_at" in cart and isinstance(cart["updated_at"], datetime):
        cart["updated_at"] = cart["updated_at"].isoformat()
    if "items" in cart:
        for item in cart["items"]:
            if "product_id" in item:
                item["product_id"] = str(item["product_id"])
    return cart

@router.get("/")
async def get_cart(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    cart = await db.carts.find_one({"user_id": user_id})
    
    if not cart:
        new_cart = {
            "user_id": user_id,
            "items": [],
            "total_price": 0.0,
            "updated_at": datetime.utcnow()
        }
        await db.carts.insert_one(new_cart)
        cart = new_cart
        
    return JSONResponse(content=serialise_cart(cart))

@router.post("/add/")
@router.post("/add")
async def add_to_cart(request: Request, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    product_id = body.get("product_id")
    quantity = int(body.get("quantity", 1))
    
    if not product_id or not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")

    cart = await db.carts.find_one({"user_id": user_id})
    if not cart:
        cart = {"user_id": user_id, "items": [], "total_price": 0.0}

    items = cart.get("items", [])
    item_exists = False
    for cart_item in items:
        if str(cart_item["product_id"]) == str(product_id):
            cart_item["quantity"] += quantity
            item_exists = True
            break
            
    if not item_exists:
        items.append({"product_id": str(product_id), "quantity": quantity})

    # Recalculate total price
    total_price = 0.0
    for c_item in items:
        p = await db.products.find_one({"_id": ObjectId(c_item["product_id"])})
        if p:
            total_price += float(p["price"]) * int(c_item["quantity"])

    updated_at = datetime.utcnow()
    await db.carts.update_one(
        {"user_id": user_id},
        {"$set": {"items": items, "total_price": total_price, "updated_at": updated_at}},
        upsert=True
    )
    
    return JSONResponse(content={"message": "Success", "total": total_price})

@router.put("/update/")
@router.put("/update")
async def update_cart_item(request: Request, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    product_id = body.get("product_id")
    quantity = int(body.get("quantity", 0))

    cart = await db.carts.find_one({"user_id": user_id})
    if not cart:
        raise HTTPException(status_code=404, detail="No cart")

    items = cart.get("items", [])
    for cart_item in items:
        if str(cart_item["product_id"]) == str(product_id):
            cart_item["quantity"] = quantity
            break

    total_price = 0.0
    for c_item in items:
        p = await db.products.find_one({"_id": ObjectId(c_item["product_id"])})
        if p:
            total_price += float(p["price"]) * int(c_item["quantity"])

    await db.carts.update_one(
        {"user_id": user_id},
        {"$set": {"items": items, "total_price": total_price, "updated_at": datetime.utcnow()}}
    )
    return JSONResponse(content={"message": "Updated"})

@router.delete("/remove/{product_id}/")
@router.delete("/remove/{product_id}")
async def remove_from_cart(product_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    cart = await db.carts.find_one({"user_id": user_id})
    if not cart:
        raise HTTPException(status_code=404, detail="No cart")

    items = [item for item in cart.get("items", []) if str(item["product_id"]) != str(product_id)]

    total_price = 0.0
    for c_item in items:
        p = await db.products.find_one({"_id": ObjectId(c_item["product_id"])})
        if p:
            total_price += float(p["price"]) * int(c_item["quantity"])

    await db.carts.update_one(
        {"user_id": user_id},
        {"$set": {"items": items, "total_price": total_price, "updated_at": datetime.utcnow()}}
    )
    return JSONResponse(content={"message": "Removed"})
