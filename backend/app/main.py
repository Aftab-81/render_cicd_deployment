"""
Gemini API backend.

Run locally with:
    uvicorn app.main:app --reload --app-dir backend

In production (Render), this is started via:
    uvicorn app.main:app --host 0.0.0.0 --port $PORT
"""

import base64
import logging
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .gemini_client import call_gemini, extract_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gemini API Backend")

# Frontend is served from the same origin as the API (see mount at the
# bottom of this file), so CORS is only relevant if you later split the
# frontend into its own Render Static Site.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/summarize")
def summarize(text: str = Form(...)):
    logger.info("Summarization request received (%d chars)", len(text))
    prompt = f"Summarize the following paragraph:\n{text}"
    data = call_gemini([{"parts": [{"text": prompt}]}])
    return JSONResponse({"summary": extract_text(data)})


@app.post("/api/explain-image")
def explain_image(file: UploadFile = File(...)):
    image_bytes = file.file.read()
    image_b64 = base64.b64encode(image_bytes).decode()
    contents = [
        {
            "parts": [
                {"text": "Explain the content of this image."},
                {"inline_data": {"mime_type": file.content_type, "data": image_b64}},
            ]
        }
    ]
    data = call_gemini(contents)
    return JSONResponse({"explanation": extract_text(data)})


@app.post("/api/chat")
def chat(message: str = Form(...)):
    if message.lower() in ["quit", "exit"]:
        return JSONResponse({"response": "Session ended."})
    prompt = f"You are a helpful QA bot. Answer the following:\n{message}"
    data = call_gemini([{"parts": [{"text": prompt}]}])
    return JSONResponse({"response": extract_text(data)})


# Checking CICD Pipe

@app.get("/status")
def check_pipeline():
    return {"message": "CICD Pipeline is working Fine on it"}


# Serve the static frontend (index.html, style.css) from the same service.
# Declared last so it acts as a fallback and doesn't shadow the /api routes above.
_frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if _frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")
