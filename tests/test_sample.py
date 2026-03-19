from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.logger import get_logger
from app.main import app

logger = get_logger(__name__)

client = TestClient(app)


@patch("app.services.sample_service.get_llm_response")
def test_evaluate_rating_success(mock_llm):
    mock_llm.return_value = """
    {
        "dm_rating": 5,
        "reporter_rating": 4,
        "feedback": "Good understanding"
    }
    """

    payload = {"dm_response": "Explains Good", "reporter_response": "Understood Good"}

    response = client.post("/api/v1/evaluate", json=payload)
    logger.info("Waiting for response")
    assert response.status_code == 200

    data = response.json()
    assert data["dm_rating"] == 5
    assert data["reporter_rating"] == 4
