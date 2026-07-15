import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="MedGuard AI")

UPLOAD_DIR = Path(__file__).parent / "uploads"


@app.get("/")
def health_check():
    # Simple route to confirm the server is alive.
    return {"status": "Backend Running"}


@app.post("/upload")
async def upload_bill(file: UploadFile = File(...)):
    # Build the destination path inside uploads/
    destination = UPLOAD_DIR / file.filename

    # Save the uploaded file to disk
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # No AI call here yet - this endpoint only proves the file arrived and saved correctly
    return {
        "status": "uploaded",
        "filename": file.filename
    }