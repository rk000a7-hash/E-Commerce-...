from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, products, cart, order
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title="Ecommerce API")

# Setup CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(order.router)

@app.get("/")
def root():
    return {"message": "Welcome to Ecommerce API"}
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
