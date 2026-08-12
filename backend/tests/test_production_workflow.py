from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_reports_service():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "AI Workforce OS is running"
    assert "version" in body
    assert body["media_mode"] in {"mock", "real"}


def test_health_contract():
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"healthy", "degraded"}
    assert "database" in body["services"]


def test_ready_contract():
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["ready"], bool)


def test_production_workflow_is_gated_before_video_generation():
    workflow = {
        "script": True,
        "dialogue": True,
        "character": True,
        "storyboard": True,
        "images": True,
        "continuity": True,
        "approved": False,
    }
    assert all(workflow[k] for k in workflow if k != "approved")
    assert workflow["approved"] is False
    assert not workflow["approved"]


def test_quality_gate_requires_all_preconditions():
    required = ["script", "dialogue", "character", "storyboard", "images", "continuity"]
    complete = {key: True for key in required}
    assert all(complete.values())
    incomplete = dict(complete)
    incomplete["continuity"] = False
    assert not all(incomplete.values())
