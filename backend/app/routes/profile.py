from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from backend.app.deps import get_current_user
from pymongo import MongoClient

router = APIRouter()

client = MongoClient("mongodb://localhost:27017/")
db = client["CodeForgedb"]
users_collection = db["users"]

# Define a Pydantic model for user profile
class UserProfileUpdate(BaseModel):
    first_name: str
    last_name: str
    email: str
    role: str  # Instead of phone, use role
    profile_picture_url: str

@router.get("/profile-info", response_model=UserProfileUpdate)
async def get_profile_data(current_user: dict = Depends(get_current_user)):
    # Fetch the current user's profile from MongoDB
    user = users_collection.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserProfileUpdate(
        first_name=user["first_name"],
        last_name=user["last_name"],
        email=user["email"],
        role=user.get("role", ""),  # Fetch role instead of phone
        profile_picture_url=user.get("profile_picture", "")
    )

@router.post("/profile-info", response_model=UserProfileUpdate)
async def update_profile(data: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    # Update the user's profile in MongoDB
    updated_data = {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "role": data.role,  # Update the role
        "profile_picture_url": data.profile_picture_url
    }

    # Update the user document
    result = users_collection.update_one({"email": current_user["email"]}, {"$set": updated_data})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return data
