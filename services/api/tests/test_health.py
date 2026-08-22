from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_non_sensitive_service_metadata() -> None:
    response = TestClient(app).get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "English Pet Care Plan API",
        "environment": "development",
    }
