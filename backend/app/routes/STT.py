from fastapi import  File, UploadFile ,APIRouter
import whisper
import tempfile
import os

router = APIRouter()

# Load Whisper model once
model = whisper.load_model("tiny")

@router.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(await file.read())
            temp_audio_path = temp_audio.name

        # Transcribe the audio
        result = model.transcribe(temp_audio_path)
        transcription = result["text"]

        # Cleanup
        os.remove(temp_audio_path)

        return {"text": transcription}

    except Exception as e:
        return {"error": str(e)}
