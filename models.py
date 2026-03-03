"""
E-Commerce API Models
Helper functions and schema descriptions for MongoDB collections
"""

from datetime import datetime


# ==================== SCHEMA DESCRIPTIONS ====================

"""
User Schema:
{
    "_id": ObjectId,
    "email": str,           # User's email address (unique identifier)
    "created_at": datetime  # Account creation timestamp
}

OTP Schema:
{
    "_id": ObjectId,
    "email": str,           # Email address the OTP was sent to
    "otp": str,             # 6-digit OTP code
    "created_at": datetime, # OTP generation timestamp
    "verified": bool        # Whether the OTP has been used/verified
}

Product Schema:
{
    "_id": ObjectId,
    "name": str,            # Product name
    "description": str,     # Product description
    "price": float,         # Product price
    "category": str,        # Product category
    "stock": int,           # Available stock quantity
    "image_url": str        # URL to product image
}

Cart Schema:
{
    "_id": ObjectId,
    "user_email": str,      # Email of the cart owner
    "items": [              # Array of cart items
        {
            "product_name": str,  # Name of the product
            "quantity": int,      # Quantity in cart
            "price": float        # Price at time of adding
        }
    ]
}
"""


# ==================== HELPER FUNCTIONS ====================

def create_user(email: str) -> dict:
    """
    Create a properly structured user document.
    
    Args:
        email: User's email address
        
    Returns:
        dict: User document ready for MongoDB insertion
    """
    return {
        "email": email.strip().lower(),
        "created_at": datetime.utcnow()
    }


def create_otp_record(email: str, otp: str) -> dict:
    """
    Create a properly structured OTP document.
    
    Args:
        email: Email address to send OTP to
        otp: 6-digit OTP code
        
    Returns:
        dict: OTP document ready for MongoDB insertion
    """
    return {
        "email": email.strip().lower(),
        "otp": otp,
        "created_at": datetime.utcnow(),
        "verified": False
    }


def create_product(
    name: str,
    description: str,
    price: float,
    category: str,
    stock: int,
    image_url: str
) -> dict:
    """
    Create a properly structured product document.
    
    Args:
        name: Product name
        description: Product description
        price: Product price
        category: Product category
        stock: Available stock quantity
        image_url: URL to product image
        
    Returns:
        dict: Product document ready for MongoDB insertion
    """
    return {
        "name": name,
        "description": description,
        "price": float(price),
        "category": category,
        "stock": int(stock),
        "image_url": image_url
    }


def create_cart_item(product_name: str, quantity: int, price: float) -> dict:
    """
    Create a properly structured cart item.
    
    Args:
        product_name: Name of the product
        quantity: Quantity to add to cart
        price: Price of the product
        
    Returns:
        dict: Cart item document
    """
    return {
        "product_name": product_name,
        "quantity": int(quantity),
        "price": float(price)
    }


def create_cart(user_email: str, items: list = None) -> dict:
    """
    Create a properly structured cart document.
    
    Args:
        user_email: Email of the cart owner
        items: List of cart items (optional)
        
    Returns:
        dict: Cart document ready for MongoDB insertion
    """
    return {
        "user_email": user_email.strip().lower(),
        "items": items if items is not None else []
    }


# ==================== VALIDATION HELPERS ====================

def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email appears valid
    """
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip()
    
    # Basic checks
    if '@' not in email or '.' not in email:
        return False
    
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    local_part, domain = parts
    if not local_part or not domain:
        return False
    
    if '.' not in domain:
        return False
    
    return True


def validate_otp(otp: str) -> bool:
    """
    Validate OTP format.
    
    Args:
        otp: OTP code to validate
        
    Returns:
        bool: True if OTP is valid 6-digit string
    """
    if not otp or not isinstance(otp, str):
        return False
    
    otp = otp.strip()
    
    if len(otp) != 6:
        return False
    
    if not otp.isdigit():
        return False
    
    return True


def validate_quantity(quantity) -> bool:
    """
    Validate quantity value.
    
    Args:
        quantity: Quantity value to validate
        
    Returns:
        bool: True if quantity is a positive integer
    """
    try:
        qty = int(quantity)
        return qty > 0
    except (ValueError, TypeError):
        return False


def validate_price(price) -> bool:
    """
    Validate price value.
    
    Args:
        price: Price value to validate
        
    Returns:
        bool: True if price is a positive number
    """
    try:
        p = float(price)
        return p >= 0
    except (ValueError, TypeError):
        return False


# ==================== SERIALIZATION HELPERS ====================

def serialize_product(product: dict) -> dict:
    """
    Serialize a product document for JSON response.
    
    Args:
        product: Product document from MongoDB
        
    Returns:
        dict: Serialized product with string _id
    """
    if product is None:
        return None
    
    serialized = product.copy()
    if '_id' in serialized:
        serialized['_id'] = str(serialized['_id'])
    
    return serialized


def serialize_cart(cart: dict) -> dict:
    """
    Serialize a cart document for JSON response.
    
    Args:
        cart: Cart document from MongoDB
        
    Returns:
        dict: Serialized cart with string _id
    """
    if cart is None:
        return None
    
    serialized = cart.copy()
    if '_id' in serialized:
        serialized['_id'] = str(serialized['_id'])
    
    return serialized


def serialize_user(user: dict) -> dict:
    """
    Serialize a user document for JSON response.
    
    Args:
        user: User document from MongoDB
        
    Returns:
        dict: Serialized user with string _id and ISO datetime
    """
    if user is None:
        return None
    
    serialized = user.copy()
    if '_id' in serialized:
        serialized['_id'] = str(serialized['_id'])
    
    if 'created_at' in serialized and isinstance(serialized['created_at'], datetime):
        serialized['created_at'] = serialized['created_at'].isoformat()
    
    return serialized
