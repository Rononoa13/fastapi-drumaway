from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request
from fastapi.staticfiles import StaticFiles
import shutil
import os

from config import UPLOAD_DIR, BASE_DIR, OUTPUT_DIR
from services.audio_processor import AudioProcessor


app = FastAPI()
# Mount the outputs folder to play audio locally.
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

templates = Jinja2Templates(directory=(f"{BASE_DIR}/templates"))
# Initialize processor
processor = AudioProcessor()

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request, drums: str = None, rest: str = None):
    # results = getattr(app.state, "last_results", None)
    # print(results)
    results = None
    if drums and rest:
        results = {
            "drums": drums,
            "rest": rest
        }
    return templates.TemplateResponse("index.html", {"request": request, "results": results})

# @app.post("/upload")
# async def upload_audio(file: UploadFile = File(...)):

#     upload_path = UPLOAD_DIR / file.filename
#     # Save file
#     with open(upload_path, "wb") as f:
#         f.write(await file.read())
#     # Async processing
#     results = await processor.separate_drums_async(upload_path)
#     return {
#         "drums_file": str(results["drums"]),
#         "rest_file": str(results["rest"])
#     }
@app.post("/upload")
def upload_audio(file: UploadFile = File(...)):
    # Check if file is provided
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No file provided")
    
    # Check if file is audio
    ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.flac'}
    if not any(file.filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid file type. Allowed file extensions: {ALLOWED_EXTENSIONS}")
    
    # Save the uploaded file
    upload_path = UPLOAD_DIR / file.filename
    output_path = OUTPUT_DIR / file.filename
    print("upload_path -> ", upload_path)
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

        
    # Process audio
    processor = AudioProcessor(output_dir=OUTPUT_DIR)
    # processor.separate_drums(upload_path)

    # Return drumless track for download
    # return FileResponse(
    #     path=drumless_path,
    #     filename=f"{file.filename}_drumless",
    #     media_type="audio/mpeg"  # You can adjust based on file type
    # )
    results = processor.separate_drums(upload_path)

    # Pass results into state so index can render it
    # Redirect back to index with query params
    return RedirectResponse(
        url=f"/?drums={results['drums'].name}&rest={results['rest'].name}",
        status_code=status.HTTP_303_SEE_OTHER
    )
    # return {
    #         "drums_file": results["drums"].name,
    #         "rest_file": results["rest"].name
    #     }

@app.get("/home")
def home(request: Request):
    pass