import logging

import requests

from . import config

logger = logging.getLogger(__name__)


def call_gemini(contents: list) -> dict:
    """Send a request to the Gemini API and return the parsed JSON response.

    The API key is sent as a header instead of a URL query param, so it
    never ends up in server access logs or error messages that echo the URL.
    """
    headers = {
        "x-goog-api-key": config.GEMINI_API_KEY,
        "Content-Type": "application/json",
    }
    response = requests.post(
        config.GEMINI_API_URL,
        json={"contents": contents},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def extract_text(data: dict) -> str:
    """Pull the generated text out of a Gemini response, or a readable error."""
    if "candidates" in data:
        return (
            data["candidates"][0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "Error")
        )
    error_msg = data.get("error", {}).get("message", str(data))
    logger.error("Gemini API error: %s", error_msg)
    return f"Gemini API Error: {error_msg}"
