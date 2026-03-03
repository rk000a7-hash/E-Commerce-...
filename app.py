"""
E-Commerce REST API Backend
Flask application with MongoDB, OTP authentication, and cart management
"""

from flask import Flask, session, request, jsonify
from flask_mail import Mail, Message
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import random
from datetime import datetime, timedelta
from waitress import serve

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# App configuration from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

# Initialize Flask-Mail
mail = Mail(app)

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'ecommerce_db')

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Collections
    users_collection = db['users']
    otps_collection = db['otps']
    products_collection = db['products']
    carts_collection = db['carts']
    
    print(f"Connected to MongoDB: {DB_NAME}")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    raise


def seed_sample_products():
    """Seed sample products if the products collection is empty"""
    try:
        if products_collection.count_documents({}) == 0:
            sample_products = [
                {
                    "name": "Wireless Bluetooth Headphones",
                    "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life.",
                    "price": 79.99,
                    "category": "Electronics",
                    "stock": 150,
                    "image_url": "https://example.com/images/headphones.jpg"
                },
                {
                    "name": "Organic Cotton T-Shirt",
                    "description": "Comfortable and eco-friendly organic cotton t-shirt available in multiple colors.",
                    "price": 24.99,
                    "category": "Clothing",
                    "stock": 300,
                    "image_url": "https://example.com/images/tshirt.jpg"
                },
                {
                    "name": "Stainless Steel Water Bottle",
                    "description": "Double-walled insulated water bottle that keeps drinks cold for 24 hours.",
                    "price": 19.99,
                    "category": "Home & Kitchen",
                    "stock": 200,
                    "image_url": "https://example.com/images/waterbottle.jpg"
                },
                {
                    "name": "Smart Fitness Watch",
                    "description": "Track your fitness goals with heart rate monitoring, GPS, and sleep tracking.",
                    "price": 149.99,
                    "category": "Electronics",
                    "stock": 75,
                    "image_url": "https://example.com/images/smartwatch.jpg"
                },
                {
                    "name": "Leather Wallet",
                    "description": "Genuine leather wallet with RFID blocking technology and multiple card slots.",
                    "price": 39.99,
                    "category": "Accessories",
                    "stock": 120,
                    "image_url": "https://example.com/images/wallet.jpg"
                },
                {
                    "name": "Portable Bluetooth Speaker",
                    "description": "Compact waterproof speaker with powerful bass and 12-hour playtime.",
                    "price": 49.99,
                    "category": "Electronics",
                    "stock": 180,
                    "image_url": "https://example.com/images/speaker.jpg"
                }
            ]
            
            products_collection.insert_many(sample_products)
            print("Sample products seeded successfully!")
    except Exception as e:
        print(f"Error seeding products: {e}")


# Seed products on startup
seed_sample_products()


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to the provided email address"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({"error": "Email is required"}), 400
        
        email = data['email'].strip().lower()
        
        if not email:
            return jsonify({"error": "Email cannot be empty"}), 400
        
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Store OTP in database
        otp_record = {
            "email": email,
            "otp": otp,
            "created_at": datetime.utcnow(),
            "verified": False
        }
        otps_collection.insert_one(otp_record)
        
        # Send OTP via email
        try:
            msg = Message(
                subject="Your E-Commerce Login OTP",
                recipients=[email],
                body=f"Your OTP for login is: {otp}\n\nThis OTP is valid for 10 minutes.\n\nIf you did not request this, please ignore this email."
            )
            mail.send(msg)
        except Exception as mail_error:
            print(f"Failed to send email: {mail_error}")
            return jsonify({"error": "Failed to send OTP email. Please try again."}), 500
        
        return jsonify({"message": "OTP sent successfully to your email"}), 200
        
    except Exception as e:
        print(f"Error in send_otp: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    """Verify the OTP and log in the user"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'otp' not in data:
            return jsonify({"error": "Email and OTP are required"}), 400
        
        email = data['email'].strip().lower()
        otp = data['otp'].strip()
        
        if not email or not otp:
            return jsonify({"error": "Email and OTP cannot be empty"}), 400
        
        # Fetch the latest unverified OTP for this email
        otp_record = otps_collection.find_one(
            {"email": email, "verified": False},
            sort=[("created_at", -1)]
        )
        
        if not otp_record:
            return jsonify({"error": "No OTP found for this email. Please request a new OTP."}), 404
        
        # Check if OTP matches
        if otp_record['otp'] != otp:
            return jsonify({"error": "Invalid OTP"}), 400
        
        # Check if OTP is expired (10 minutes validity)
        otp_age = datetime.utcnow() - otp_record['created_at']
        if otp_age > timedelta(minutes=10):
            return jsonify({"error": "OTP has expired. Please request a new OTP."}), 400
        
        # Mark OTP as verified
        otps_collection.update_one(
            {"_id": otp_record['_id']},
            {"$set": {"verified": True}}
        )
        
        # Upsert user in users collection
        users_collection.update_one(
            {"email": email},
            {"$setOnInsert": {"email": email, "created_at": datetime.utcnow()}},
            upsert=True
        )
        
        # Set session
        session['user_email'] = email
        
        return jsonify({"message": "Login successful", "email": email}), 200
        
    except Exception as e:
        print(f"Error in verify_otp: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if the user is authenticated"""
    try:
        if 'user_email' in session:
            return jsonify({
                "authenticated": True,
                "email": session['user_email']
            }), 200
        else:
            return jsonify({"authenticated": False}), 200
            
    except Exception as e:
        print(f"Error in check_auth: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """Log out the current user"""
    try:
        session.clear()
        return jsonify({"message": "Logged out successfully"}), 200
        
    except Exception as e:
        print(f"Error in logout: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ==================== PRODUCT ENDPOINTS ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        products = list(products_collection.find({}))
        
        # Convert ObjectId to string for JSON serialization
        for product in products:
            product['_id'] = str(product['_id'])
        
        return jsonify({"products": products}), 200
        
    except Exception as e:
        print(f"Error in get_products: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ==================== CART ENDPOINTS ====================

def is_authenticated():
    """Helper function to check if user is authenticated"""
    return 'user_email' in session


@app.route('/api/cart', methods=['GET'])
def get_cart():
    """Get the current user's cart"""
    try:
        if not is_authenticated():
            return jsonify({"error": "Authentication required"}), 401
        
        user_email = session['user_email']
        
        cart = carts_collection.find_one({"user_email": user_email})
        
        if cart:
            cart['_id'] = str(cart['_id'])
            return jsonify({"cart": cart.get('items', [])}), 200
        else:
            return jsonify({"cart": []}), 200
            
    except Exception as e:
        print(f"Error in get_cart: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """Add a product to the cart"""
    try:
        if not is_authenticated():
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.get_json()
        
        if not data or 'product_name' not in data or 'quantity' not in data:
            return jsonify({"error": "Product name and quantity are required"}), 400
        
        product_name = data['product_name']
        quantity = int(data['quantity'])
        
        if quantity <= 0:
            return jsonify({"error": "Quantity must be greater than 0"}), 400
        
        # Validate product exists
        product = products_collection.find_one({"name": product_name})
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        user_email = session['user_email']
        
        # Check if cart exists and product is already in cart
        existing_cart = carts_collection.find_one({"user_email": user_email})
        
        if existing_cart:
            # Check if product already in cart
            product_in_cart = False
            for item in existing_cart.get('items', []):
                if item['product_name'] == product_name:
                    product_in_cart = True
                    break
            
            if product_in_cart:
                # Increment quantity
                carts_collection.update_one(
                    {"user_email": user_email, "items.product_name": product_name},
                    {"$inc": {"items.$.quantity": quantity}}
                )
            else:
                # Push new item
                carts_collection.update_one(
                    {"user_email": user_email},
                    {"$push": {"items": {
                        "product_name": product_name,
                        "quantity": quantity,
                        "price": product['price']
                    }}}
                )
        else:
            # Create new cart
            carts_collection.insert_one({
                "user_email": user_email,
                "items": [{
                    "product_name": product_name,
                    "quantity": quantity,
                    "price": product['price']
                }]
            })
        
        return jsonify({"message": "Product added to cart successfully"}), 200
        
    except ValueError:
        return jsonify({"error": "Invalid quantity value"}), 400
    except Exception as e:
        print(f"Error in add_to_cart: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    """Remove a product from the cart"""
    try:
        if not is_authenticated():
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.get_json()
        
        if not data or 'product_name' not in data:
            return jsonify({"error": "Product name is required"}), 400
        
        product_name = data['product_name']
        user_email = session['user_email']
        
        # Remove item from cart
        result = carts_collection.update_one(
            {"user_email": user_email},
            {"$pull": {"items": {"product_name": product_name}}}
        )
        
        if result.modified_count == 0:
            return jsonify({"error": "Product not found in cart"}), 404
        
        return jsonify({"message": "Product removed from cart successfully"}), 200
        
    except Exception as e:
        print(f"Error in remove_from_cart: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    """Update the quantity of a product in the cart"""
    try:
        if not is_authenticated():
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.get_json()
        
        if not data or 'product_name' not in data or 'quantity' not in data:
            return jsonify({"error": "Product name and quantity are required"}), 400
        
        product_name = data['product_name']
        quantity = int(data['quantity'])
        
        if quantity <= 0:
            return jsonify({"error": "Quantity must be greater than 0"}), 400
        
        user_email = session['user_email']
        
        # Update quantity in cart
        result = carts_collection.update_one(
            {"user_email": user_email, "items.product_name": product_name},
            {"$set": {"items.$.quantity": quantity}}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Product not found in cart"}), 404
        
        return jsonify({"message": "Cart updated successfully"}), 200
        
    except ValueError:
        return jsonify({"error": "Invalid quantity value"}), 400
    except Exception as e:
        print(f"Error in update_cart: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    print("Starting E-Commerce API Server...")
    print("Server running on http://0.0.0.0:5000")
    serve(app, host='0.0.0.0', port=5000)
