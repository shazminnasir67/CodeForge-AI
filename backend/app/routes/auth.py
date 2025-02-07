from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from backend.app.models import User, TokenSchema
from backend.app.utils import get_hashed_password, verify_password, create_access_token, create_refresh_token
from backend.app.deps import get_current_user
from pymongo import MongoClient
import os
from fastapi import File, UploadFile, HTTPException, Form
from PIL import Image
import io
import os
from uuid import uuid4
from pathlib import Path
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

router = APIRouter()

client = MongoClient("mongodb://localhost:27017/")
db = client["CodeForgedb"]
users_collection = db["users"]
templates = Jinja2Templates(directory="frontend/templates")
config = Config("backend/app/.env")
oauth = OAuth(config)
oauth.register(
    name="github",
    client_id=os.getenv("Client_id"),
    client_secret=os.getenv("Client_secret_id"),
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://accounts.google.com/o/oauth2/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "email profile"},
)
UPLOAD_FOLDER = "uploads"  # Directory to store profile images
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)  # Ensure folder exists

@router.post("/register")
async def register(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    profile_picture: UploadFile = File(None)
):
    # Check if the user already exists
    user_exists = users_collection.find_one({"email": email})
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid4())

    profile_picture_url = "/frontend/static/img/user.jpg"  # Default image path
    if profile_picture:
        content = await profile_picture.read()  # Read the file content
        file_size = len(content)  # Check the size of the file in bytes
        if file_size > 2 * 1024 * 1024:  # Max file size: 2MB
            raise HTTPException(status_code=400, detail="Profile picture too large (max 2MB)")

    # Save the uploaded profile picture
    unique_filename = f"{uuid4()}.{profile_picture.filename.split('.')[-1]}"
    image_path = os.path.join(UPLOAD_FOLDER, unique_filename)  # Path where the image will be stored

    try:
        # Verify and resize the image (optional)
        image = Image.open(io.BytesIO(content))
        image.verify()  # Verify it's a valid image
        image = Image.open(io.BytesIO(content))  # Reload image to process and resize
        image.thumbnail((500, 500))  # Resize to 500x500 pixels max
        image.save(image_path)  # Save the image to disk
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Set the profile picture URL to be stored in the database
    profile_picture_url = f"/{UPLOAD_FOLDER}/{unique_filename}"

    # Hash the password
    hashed_password = get_hashed_password(password)

    # Insert user into the database
    users_collection.insert_one({
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "role": role,
        "profile_picture": profile_picture_url,
        "password": hashed_password,
        "preferences": {
            "theme": "light",
            "language": "en",
            "ai_features": []
        },
        "projects": [],
        "activity_log": [],
        "total_projects": 0,
        "total_errors_fixed": 0,
        "ai_usage_stats": {
            "code_completions": 0,
            "debugging_requests": 0,
            "test_case_suggestions": 0
        },
        "last_active": None,
        "account_status": "Active",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })

    return {"message": "User registered successfully"}

ACCESS_TOKEN_EXPIRE_MINUTES = 300
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Example: 7 days


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Find the user in the database
    db_user = users_collection.find_one({"email": form_data.username})
    if not db_user or not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=db_user["email"], expires_delta=access_token_expires)

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(subject=db_user["email"], expires_delta=refresh_token_expires)

    # Prepare response with HttpOnly cookies
    response = JSONResponse({"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,  # Ensures cookies are sent only over HTTPS
        samesite="Strict",  # Prevents cross-site request forgery (CSRF)
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=True,
        samesite="Strict",
    )

    return response

@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for("auth_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google")
async def auth_google(request: Request):
    token = await oauth.google.authorize_access_token(request)
    resp = await oauth.google.get("userinfo", token=token)
    profile = resp.json()
    email = profile.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Google profile")

    # Handle user registration or login
    return {"message": "Google login successful"}

@router.get("/login/github")
async def login_github(request: Request):
    redirect_uri = request.url_for("auth_github")
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/auth/github")
async def auth_github(request: Request):
    token = await oauth.github.authorize_access_token(request)
    resp = await oauth.github.get("user", token=token)
    profile = resp.json()
    email = profile.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in GitHub profile")

    user_exists = users_collection.find_one({"email": email})
    if not user_exists:
        hashed_password = get_hashed_password(os.urandom(16).hex())
        users_collection.insert_one({"email": email, "password": hashed_password})

    access_token = create_access_token(email)
    refresh_token = create_refresh_token(email)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/logout")
async def logout():
    # Create a RedirectResponse object to redirect the user
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Clear the cookies by setting their values to an empty string and max_age to 0
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    return response
