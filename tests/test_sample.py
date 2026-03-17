from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sample():
    response = client.post("/api/v1/sample", json={"name": "Bavi"})

    assert response.status_code == 200
