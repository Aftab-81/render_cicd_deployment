import os

# Must be set before backend.app.config is imported anywhere, since it
# raises ValueError at import time if GEMINI_API_KEY is missing.
os.environ.setdefault("GEMINI_API_KEY", "test-key-for-ci")
