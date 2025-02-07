from fastapi import APIRouter, HTTPException
from backend.app.models import ImageData
import base64
from io import BytesIO
from PIL import Image
import pytesseract

router = APIRouter()

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@router.post("/api/process-image")
async def process_image(data: ImageData):
    try:
        header, encoded = data.image.split(',', 1)
        image_data = base64.b64decode(encoded)
        image = Image.open(BytesIO(image_data))
        ocr_result = pytesseract.image_to_string(image)
        return {"result": ocr_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))