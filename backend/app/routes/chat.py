import datetime
import uuid
from datetime import timedelta
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import bleach
from pymongo import MongoClient

router = APIRouter()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["CodeForgedb"]
history_collection = db["conversation_history"]

def get_session_id():
    """Generate a new session ID or get the existing one"""
    return str(uuid.uuid4())  # Unique session ID per conversation

@router.post("/api/chat")
async def chat_api(request: Request):
    try:
        # Parse and validate request body
        body = await request.json()
        messages = body.get("messages", [])
        session_id = body.get("session_id", get_session_id())
        temperature = body.get("temperature", 0.7)

        # Validate messages and temperature
        if not isinstance(messages, list):
            raise HTTPException(status_code=400, detail="Messages must be a list")
        if not isinstance(temperature, (int, float)) or not (0 <= temperature <= 2):
            raise HTTPException(status_code=400, detail="Temperature must be a float between 0 and 2")

        # Check session timeout
        current_time = datetime.datetime.utcnow()
        last_session = history_collection.find_one({"session_id": session_id})
        if last_session and last_session["timestamp"] + timedelta(minutes=30) < current_time:
            session_id = get_session_id()  # Generate new session ID if expired

        # Prepare payload for LLM
        lm_payload = {
            "model": "llama-3.2-3b-instruct",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": -1,
            "stream": False
        }

        # Call external LLM service
        async with httpx.AsyncClient(timeout=860.0) as client:
            response = await client.post("http://127.0.0.1:1234/v1/chat/completions", json=lm_payload)
            response.raise_for_status()  # Raise HTTPStatusError for bad responses
            lm_response = response.json()

        # Sanitize AI response
        allowed_tags = ["strong", "h2", "h3", "h4", "ul", "ol", "li", "br", "pre", "code"]
        ai_message = bleach.clean(lm_response['choices'][0]['message']['content'], tags=allowed_tags)

        # Save conversation history to MongoDB
        history_collection.insert_one({
            "session_id": session_id,
            "messages": messages,
            "ai_response": ai_message,
            "timestamp": current_time
        })

        # Return response to client
        return JSONResponse(content={"message": ai_message, "session_id": session_id})

    except httpx.HTTPStatusError as http_err:
        return JSONResponse(content={"error": f"HTTP error occurred: {http_err}"}, status_code=500)
    except httpx.RequestError as req_err:
        return JSONResponse(content={"error": f"Request error occurred: {req_err}"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": f"An error occurred: {e}"}, status_code=500)

@router.get("/api/history/{user_id}")
async def get_history(user_id: str):
    try:
        # Retrieve the conversation history, grouped by session_id, sorted by timestamp
        history = list(history_collection.find({"user_id": user_id}).sort("timestamp", -1))
        for entry in history:
            entry["_id"] = str(entry["_id"])  # Convert MongoDB ObjectId to string

        return JSONResponse(content={"history": history})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)