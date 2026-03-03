import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

async def clear_data():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.ecommerce
    await db.products.delete_many({})
    await db.orders.delete_many({})
    await db.carts.delete_many({})
    print("Cleared all products, orders, and carts")
    client.close()

if __name__ == "__main__":
    asyncio.run(clear_data())
