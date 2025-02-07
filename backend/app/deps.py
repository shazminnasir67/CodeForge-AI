from typing import Union, Any
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from pymongo import MongoClient
from backend.app.utils import ALGORITHM, JWT_SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


client = MongoClient("mongodb://localhost:27017/")
db = client["CodeForgedb"]
users_collection = db["users"]

from typing import Union, Any
from datetime import datetime
from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from pydantic import ValidationError
from pymongo import MongoClient
from backend.app.utils import ALGORITHM, JWT_SECRET_KEY

client = MongoClient("mongodb://localhost:27017/")
db = client["CodeForgedb"]
users_collection = db["users"]

async def get_current_user(request: Request): 
    # Extract the token from cookies
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Access token is missing.",
        )
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token. Missing 'sub'.",
            )
    except JWTError as e:
        print(f"JWT Error: {e}")  # Log decoding errors for debugging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )
    except ValidationError as e:
        print(f"Validation Error: {e}")  # Log validation errors for debugging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation error.",
        )

    # Fetch user from MongoDB
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user
