import os
from pathlib import Path
from dotenv import load_dotenv

# backend/
BASE_DIR = Path(__file__).resolve().parent.parent

# backend/.env
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Set it in your environment or .env file."
    )