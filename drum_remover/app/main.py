from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
import shutil
import os

from config import UPLOAD_DIR, BASE_DIR, OUTPUT_DIR
from services.audio_processor import AudioProcessor

app = FastAPI()
templates = Jinja2Templates(directory=(f"{BASE_DIR}/templates"))
# Initialize processor
processor = AudioProcessor()

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):

    upload_path = UPLOAD_DIR / file.filename
    # Save file
    with open(upload_path, "wb") as f:
        f.write(await file.read())
    # Async processing
    results = await processor.separate_drums_async(upload_path)
    return {
        "drums_file": str(results["drums"]),
        "rest_file": str(results["rest"])
    }
# @app.post("/upload")
# def upload_audio(file: UploadFile = File(...)):
#     # Check if file is provided
#     if not file.filename:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="No file provided")
    
#     # Check if file is audio
#     ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.flac'}
#     if not any(file.filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Invalid file type. Allowed file extensions: {ALLOWED_EXTENSIONS}")
    
#     # Save the uploaded file
#     upload_path = UPLOAD_DIR / file.filename
#     output_path = OUTPUT_DIR / file.filename
#     print("upload_path -> ", upload_path)
#     with open(upload_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

        
#     # Process audio
#     processor = AudioProcessor(output_dir=OUTPUT_DIR)
#     processor.seperate_drums(upload_path)

    # Return drumless track for download
    # return FileResponse(
    #     path=drumless_path,
    #     filename=f"{file.filename}_drumless",
    #     media_type="audio/mpeg"  # You can adjust based on file type
    # )