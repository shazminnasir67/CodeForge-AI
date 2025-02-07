from fastapi import APIRouter, UploadFile, File, HTTPException
import pdfplumber

router = APIRouter()

@router.post("/api/process-pdf")
async def process_pdf(file: UploadFile = File(...)):
    if file.filename.endswith('.pdf'):
        try:
            with pdfplumber.open(file.file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return {"result": text.strip()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a PDF file.")