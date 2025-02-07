from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from backend.app.deps import get_current_user
from backend.app.models import User
from backend.app.routes import auth, profile, user, ocr, pdf, chat, code_analysis,STT

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="frontend/templates")
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(ocr.router)
app.include_router(pdf.router)
app.include_router(chat.router)
app.include_router(code_analysis.router)
app.include_router(profile.router)
app.include_router(STT.router)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/auth/status", response_class=JSONResponse)
async def auth_status(current_user: User = Depends(get_current_user)):
    if current_user:
        return {"authenticated": True}
    return {"authenticated": False}

@app.get("/editor", response_class=HTMLResponse)
async def editor_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("Editor.html", {"request": request, "current_user": current_user})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("Chat.html", {"request": request, "current_user": current_user})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("Profile.html", {"request": request, "current_user": current_user})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

