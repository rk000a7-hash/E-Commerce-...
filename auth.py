from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.user import UserCreate, UserLogin, Token, UserModel
from database import db
from utils.security import get_password_hash, verify_password, create_access_token
from auth.dependencies import get_current_user
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = "http://localhost:5173/auth/google/callback"

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "role": "user"
    }
    
    result = await db.users.insert_one(new_user)
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not user.get("password") or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not user.get("password") or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "name": current_user["name"],
        "email": current_user["email"],
        "role": current_user.get("role", "user")
    }

@router.post("/google")
async def google_auth(token_data: dict):
    token = token_data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is missing")
    
    async with httpx.AsyncClient() as client:
        # Fetch user info from Google's userInfo endpoint using the provided access token
        response = await client.get(f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}")
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid Google token")
            
        user_info = response.json()
        
    email = user_info.get("email")
    name = user_info.get("name")
    google_id = user_info.get("sub")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")
        
    # Check if user already exists in MongoDB
    user = await db.users.find_one({"email": email})
    
    if not user:
        # Create new user if they don't exist
        new_user = {
            "name": name,
            "email": email,
            "google_id": google_id,
            "role": "user",
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(new_user)
    else:
        # Link Google ID if it's not already linked to the existing user
        if "google_id" not in user or user["google_id"] != google_id:
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"google_id": google_id}}
            )
        
    # Generate our app's JWT
    access_token = create_access_token(data={"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}
