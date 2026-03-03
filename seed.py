import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

async def seed_data():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.ecommerce
    
    products = [
        {
            "title": "Premium Wireless Headphones",
            "description": "High-quality noise-canceling wireless headphones with a long battery life, perfect for audiophiles.",
            "price": 199.99,
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
            "category": "Electronics",
            "stock": 50
        },
        {
            "title": "Minimalist Smartwatch",
            "description": "A sleek, modern smartwatch that tracks your fitness, notifications, and looks great on any wrist.",
            "price": 249.50,
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80",
            "category": "Accessories",
            "stock": 120
        },
        {
            "title": "Classic Leather Backpack",
            "description": "Durable and stylish leather backpack, ideal for commuting or short trips.",
            "price": 89.99,
            "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&q=80",
            "category": "Fashion",
            "stock": 35
        },
        {
            "title": "Professional DSLR Camera",
            "description": "Capture stunning photos and 4K videos with this versatile DSLR camera.",
            "price": 899.00,
            "image": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&q=80",
            "category": "Photography",
            "stock": 15
        }
    ]
    
    # Check if we already have products
    count = await db.products.count_documents({})
    if count == 0:
        await db.products.insert_many(products)
        print("Inserted dummy products.")
    else:
        print("Products already exist, skipping seed.")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
