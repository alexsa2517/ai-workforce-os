#!/usr/bin/env python3
"""
Example: AI Video Generation Workflow
Demonstrates how to use the Video Generation API programmatically.
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"
API_KEY = "your-api-key-here"  # Change this!

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}


async def create_project():
    """Step 1: Create a video project (Phase 1)."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/video/projects",
            headers=headers,
            json={
                "title": "Cyberpunk City Tour",
                "description": "A cinematic tour through a neon-lit cyberpunk city",
                "goal": "Create an engaging promotional video",
                "target_audience": "Sci-fi enthusiasts",
                "duration_target": 60,
                "aspect_ratio": "16:9",
                "visual_style": "Cyberpunk anime in the style of Ghost in the Shell",
                "language": "th",
            },
        )
        data = resp.json()
        print(f"✅ Project created: {data['project_id']}")
        return data["project_id"]


async def set_global_definitions(project_id: str):
    """Step 2: Define visual style, voices, and BGM (Phase 2)."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/video/projects/{project_id}/global-def",
            headers=headers,
            json={
                "style_spec": {
                    "sub_genre": "Cyberpunk anime",
                    "rendering_line": "2D digital painting with thin glowing outlines",
                    "color_lighting": "High saturation neon (pink, cyan, purple), dark backgrounds, rim lighting",
                    "detail_density": "Highly detailed backgrounds, moderate character detail",
                },
                "voice_profiles": {
                    "narrator": {
                        "name": "Narrator",
                        "gender": "female",
                        "tone": "professional",
                        "pace": "moderate",
                        "language": "th",
                    }
                },
                "bgm_source": "separate",
                "bgm_properties": {
                    "genre_style": "Cinematic electronic",
                    "bpm": 120,
                    "key_scale": "C minor",
                    "core_instrumentation": ["synthesizer", "strings", "piano", "bass"],
                    "soundscape": "urban night atmosphere",
                    "production_quality": "studio",
                },
            },
        )
        print(f"✅ Global definitions set: {resp.json()['current_phase']}")


async def plan_clips(project_id: str):
    """Step 3: Generate clip plans using LLM (Phase 3)."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/video/projects/{project_id}/plan-clips",
            headers=headers,
            params={"provider": "openai"},
        )
        data = resp.json()
        print(f"✅ Clips planned: {len(data['clips'])} clips")
        for clip in data["clips"]:
            print(f"  - Clip {clip['sequence_number']}: {clip['scene'][:50]}...")
        return data


async def generate_bgm_blueprint(project_id: str):
    """Generate BGM emotional arc blueprint."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/video/projects/{project_id}/bgm-blueprint",
            headers=headers,
        )
        data = resp.json()
        print(f"✅ BGM Blueprint generated: {data['total_duration']}s, {data['bpm']} BPM")
        return data


async def run_pipeline(project_id: str):
    """Run full pipeline (Phases 2-5)."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/video/projects/{project_id}/run-pipeline",
            headers=headers,
            json={
                "style_spec": {
                    "sub_genre": "Cyberpunk anime",
                    "rendering_line": "2D digital painting with thin glowing outlines",
                    "color_lighting": "High saturation neon, dark backgrounds, rim lighting",
                    "detail_density": "Highly detailed backgrounds",
                },
                "voice_profiles": {},
                "bgm_source": "separate",
                "bgm_properties": {
                    "genre_style": "Cinematic electronic",
                    "bpm": 120,
                    "key_scale": "C minor",
                    "core_instrumentation": ["synthesizer", "strings"],
                },
            },
            params={"provider": "openai"},
        )
        data = resp.json()
        print(f"✅ Pipeline complete: {data['status']} - {data['message']}")
        return data


async def main():
    """Run complete video generation example."""
    print("🎬 AI Workforce OS - Video Generation Example\n")

    # Step 1: Create project
    project_id = await create_project()

    # Step 2: Set global definitions
    await set_global_definitions(project_id)

    # Step 3: Plan clips
    await plan_clips(project_id)

    # Step 4: Generate BGM blueprint
    await generate_bgm_blueprint(project_id)

    # Alternative: Run full pipeline at once
    # await run_pipeline(project_id)

    print(f"\n🎉 Done! Project ID: {project_id}")
    print(f"📊 Check status: {BASE_URL}/api/v1/video/projects/{project_id}")


if __name__ == "__main__":
    asyncio.run(main())
