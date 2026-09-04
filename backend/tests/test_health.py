import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.init_db import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "BugForge API"
        }

def test_create_and_list_project():
    with TestClient(app) as client:
        # Test POST /api/v1/projects
        create_payload = {
            "name": "Test Project",
            "path": "c:/tmp/test_project",
            "language": "python"
        }
        res = client.post("/api/v1/projects", json=create_payload)
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "Test Project"
        assert "id" in data

        # Test GET /api/v1/projects
        list_res = client.get("/api/v1/projects")
        assert list_res.status_code == 200
        projects = list_res.json()
        assert len(projects) >= 1
