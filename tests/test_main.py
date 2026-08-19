from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("backend.app.main.call_gemini")
def test_summarize(mock_call_gemini):
    mock_call_gemini.return_value = {
        "candidates": [{"content": {"parts": [{"text": "A short summary."}]}}]
    }
    response = client.post("/api/summarize", data={"text": "Some long paragraph to summarize."})
    assert response.status_code == 200
    assert response.json() == {"summary": "A short summary."}
    mock_call_gemini.assert_called_once()


@patch("backend.app.main.call_gemini")
def test_summarize_handles_api_error(mock_call_gemini):
    mock_call_gemini.return_value = {"error": {"message": "quota exceeded"}}
    response = client.post("/api/summarize", data={"text": "Anything"})
    assert response.status_code == 200
    assert "quota exceeded" in response.json()["summary"]


def test_chat_quit_short_circuits_without_calling_gemini():
    with patch("backend.app.main.call_gemini") as mock_call_gemini:
        response = client.post("/api/chat", data={"message": "quit"})
        assert response.status_code == 200
        assert response.json() == {"response": "Session ended."}
        mock_call_gemini.assert_not_called()
