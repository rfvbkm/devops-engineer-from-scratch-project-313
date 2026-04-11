from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_ping_returns_pong() -> None:
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert response.text == "pong"
