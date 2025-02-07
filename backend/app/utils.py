import os
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Union, Any
from dotenv import load_dotenv
from jose import jwt

# Load environment variables from .env file
load_dotenv(dotenv_path="backend/app/.env")

# Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 70  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")


# Ensure the keys are strings
if not isinstance(JWT_SECRET_KEY, str) or not isinstance(JWT_REFRESH_SECRET_KEY, str):
    raise ValueError("JWT_SECRET_KEY and JWT_REFRESH_SECRET_KEY must be strings")

# Password hashing
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    expires_delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expires = datetime.now(timezone.utc) + expires_delta

    to_encode = {"exp": expires, "sub": str(subject)}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    expires_delta = expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    expires = datetime.now(timezone.utc) + expires_delta

    to_encode = {"exp": expires, "sub": str(subject)}
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)


