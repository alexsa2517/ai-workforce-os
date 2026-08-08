"""
Video Generation System Tests
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_video_project(client):
    """Test creating a video project."""
    response = await client.post("/api/v1/video/projects", json={
        "title": "Test Video Project",
        "description": "A test video for unit testing",
        "goal": "Test the video generation API",
        "duration_target": 30,
        "aspect_ratio": "16:9",
        "language": "th",
    }, headers={"X-API-Key": "dev-api-key-change-in-production"})

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Video Project"
    assert data["status"] == "draft"
    assert data["current_phase"] == "initial"
    assert "project_id" in data


@pytest.mark.asyncio
async def test_list_video_projects(client):
    """Test listing video projects."""
    response = await client.get("/api/v1/video/projects")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_video_project_lifecycle(client):
    """Test full video project lifecycle."""
    # 1. Create project
    create_resp = await client.post("/api/v1/video/projects", json={
        "title": "Lifecycle Test",
        "duration_target": 15,
        "aspect_ratio": "16:9",
    }, headers={"X-API-Key": "dev-api-key-change-in-production"})

    assert create_resp.status_code == 201
    project = create_resp.json()
    project_id = project["project_id"]

    # 2. Set global definitions
    global_def_resp = await client.post(
        f"/api/v1/video/projects/{project_id}/global-def",
        json={
            "style_spec": {
                "sub_genre": "Cyberpunk anime",
                "rendering_line": "2D digital painting, thin glowing outlines",
                "color_lighting": "High saturation neon, dark backgrounds, rim lighting",
                "detail_density": "Highly detailed backgrounds",
            },
            "voice_profiles": {},
            "bgm_source": "separate",
            "bgm_properties": {
                "genre_style": "Cinematic electronic",
                "bpm": 120,
                "key_scale": "C minor",
                "core_instrumentation": ["synthesizer", "strings", "piano"],
            },
        },
        headers={"X-API-Key": "dev-api-key-change-in-production"},
    )

    assert global_def_resp.status_code == 200
    assert global_def_resp.json()["current_phase"] == "global_def"

    # 3. Get project
    get_resp = await client.get(f"/api/v1/video/projects/{project_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["project_id"] == project_id

    # 4. Delete project
    del_resp = await client.delete(f"/api/v1/video/projects/{project_id}")
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_video_project_not_found(client):
    """Test getting non-existent project."""
    response = await client.get("/api/v1/video/projects/nonexistent-id")
    assert response.status_code == 404
