import json
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException

from ai_service import extract_bill_data, generate_complaint
from analyzer import analyze_line_items, compute_transparency_score
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="MedGuard AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://YOUR-FRONTEND-URL.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def health_check():
    return {"status": "Backend Running"}


@app.post("/upload")
async def upload_bill(file: UploadFile = File(...)):
    destination = UPLOAD_DIR / file.filename
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {
        "status": "uploaded",
        "filename": file.filename
    }


def parse_gemini_json(raw_text: str) -> dict:
    """
    Gemini is instructed to return raw JSON, but occasionally wraps it in
    markdown code fences anyway. Strip those defensively before parsing,
    rather than assuming clean output every time.
    """
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1).replace("json", "", 1)
        cleaned = cleaned.strip()
    return json.loads(cleaned)


@app.post("/analyze")
async def analyze_bill(filename: str):
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found. Upload it first via /upload.")

    try:
        raw_result = extract_bill_data(str(file_path))
    except Exception:
        raise HTTPException(status_code=503, detail="AI service is temporarily unavailable. Please try again in a moment.")

    try:
        extracted = parse_gemini_json(raw_result)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="AI extraction returned invalid JSON. Try again.")

    analysis = analyze_line_items(extracted.get("line_items", []))
    score_data = compute_transparency_score(analysis["findings"])

    return {
        "hospital_name": extracted.get("hospital_name"),
        "bill_date": extracted.get("bill_date"),
        "total_line_items": analysis["total_line_items"],
        "total_findings": analysis["total_findings"],
        "transparency_score": score_data["transparency_score"],
        "risk_level": score_data["risk_level"],
        "findings": analysis["findings"]
    }


@app.post("/complaint")
async def create_complaint(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")

    try:
        raw_result = extract_bill_data(str(file_path))
        extracted = parse_gemini_json(raw_result)
    except Exception:
        raise HTTPException(status_code=503, detail="AI service unavailable. Try again.")

    analysis = analyze_line_items(extracted.get("line_items", []))

    try:
        complaint_text = generate_complaint(
            extracted.get("hospital_name"),
            extracted.get("bill_date"),
            analysis["findings"]
        )
    except Exception:
        raise HTTPException(status_code=503, detail="Complaint generation failed. Try again.")

    return {"complaint_text": complaint_text}