from pydantic import BaseModel, EmailStr

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    role: str  
    password: str  
    profile_picture: Optional[str] = "/img/user.png"
    preferences: dict = {"theme": "light", "language": "en", "ai_features": []}
    projects: List[dict] = []
    activity_log: List[dict] = []
    total_projects: int = 0
    total_errors_fixed: int = 0
    ai_usage_stats: dict = {"code_completions": 0, "debugging_requests": 0, "test_case_suggestions": 0}
    last_active: Optional[datetime] = None
    account_status: str = "Active"
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class ImageData(BaseModel):
    image: str

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str