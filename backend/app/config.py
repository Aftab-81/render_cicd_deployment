import os
from dotenv import load_dotenv

load_dotenv('D:/Multiple Projects/project-fix/backend/app/.env')

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("API = ", GEMINI_API_KEY)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)

# Comma-separated list in env, e.g. "https://myapp.com,https://www.myapp.com"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Set it in your environment or .env file "
        "(see .env.example)."
    )
