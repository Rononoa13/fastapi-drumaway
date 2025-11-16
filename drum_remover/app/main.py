from fastapi import FastAPI, UploadFile, File, HTTPException, status, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request
from fastapi.staticfiles import StaticFiles
import shutil
import os

from config import UPLOAD_DIR, BASE_DIR, OUTPUT_DIR
from services.audio_processor import AudioProcessor
from services.background_tasks import detect_onsets_task


app = FastAPI()
# Mount the outputs folder to play audio locally.
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

templates = Jinja2Templates(directory=(f"{BASE_DIR}/templates"))


processor = AudioProcessor() # Initialize processor

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
def upload_audio(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
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

    results = processor.separate_drums(upload_path)
    drums_path = results["drums"]
    # Schedule onset detection in background
    if background_tasks:
        background_tasks.add_task(detect_onsets_task, drums_path)

    # Pass results into state so index can render it
    # Redirect back to index with query params
    return RedirectResponse(
        url=f"/?drums={results['drums'].name}&rest={results['rest'].name}",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/home")
def home(request: Request):
    pass