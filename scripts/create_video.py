#!/usr/bin/env python3
"""
Example: Create a REAL AI Video using the Video Generation API
This script demonstrates the complete workflow from project creation to final video.

Requirements:
- OpenAI API Key (for DALL-E 3 + TTS)
- ffmpeg installed
- Backend running at http://localhost:8000

Usage:
    export OPENAI_API_KEY=sk-...
    python scripts/create_video.py
"""
import asyncio
import httpx
import json
import time

BASE_URL = "http://localhost:8000"
API_KEY = "dev-api-key-change-in-production"  # Change to your API key

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}


async def create_project() -> str:
    """Step 1: Create a video project."""
    print("🎬 Step 1: Creating video project...")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/video/projects",
            headers=headers,
            json={
                "title": "Neon Cyberpunk City",
                "description": "A cinematic journey through a neon-lit cyberpunk metropolis at night",
                "goal": "Create an atmospheric promotional video",
                "target_audience": "Sci-fi fans and tech enthusiasts",
                "duration_target": 30,
                "aspect_ratio": "16:9",
                "visual_style": "Cyberpunk anime with neon lights and rain",
                "language": "th",
            },
        )
        data = resp.json()
        project_id = data["project_id"]
        print(f"   ✅ Project created: {project_id}")
        return project_id


async def run_pipeline(project_id: str):
    """Step 2-5: Run full pipeline in one call."""
    print("\n🚀 Step 2-5: Running full video generation pipeline...")
    print("   This will use DALL-E 3 for images, OpenAI TTS for audio, and ffmpeg for video.")

    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/video/projects/{project_id}/run-pipeline",
            headers=headers,
            json={
                "style_spec": {
                    "sub_genre": "Cyberpunk anime",
                    "rendering_line": "2D digital painting with thin glowing outlines",
                    "color_lighting": "High saturation neon (pink, cyan, purple), dark backgrounds, rim lighting, rain reflections",
                    "detail_density": "Highly detailed backgrounds with holographic advertisements",
                },
                "voice_profiles": {
                    "narrator": {
                        "name": "narrator",
                        "gender": "female",
                        "tone": "mysterious",
                        "pace": "moderate",
                        "language": "th",
                    }
                },
                "bgm_source": "separate",
                "bgm_properties": {
                    "genre_style": "Cinematic synthwave",
                    "bpm": 110,
                    "key_scale": "C minor",
                    "core_instrumentation": ["synthesizer", "bass", "electronic drums", "pad"],
                    "soundscape": "urban night rain",
                    "production_quality": "studio",
                },
            },
            params={"provider": "openai"},
        )

        status = resp.json()
        print(f"   ✅ Pipeline started: {status['message']}")
        return status


async def monitor_progress(project_id: str):
    """Monitor video generation progress."""
    print("\n⏳ Monitoring progress...")

    async with httpx.AsyncClient() as client:
        for _ in range(60):  # Check for 5 minutes max
            resp = await client.get(
                f"{BASE_URL}/api/v1/video/projects/{project_id}",
                headers=headers,
            )
            project = resp.json()

            progress = project["progress_percent"]
            phase = project["current_phase"]
            status = project["status"]

            print(f"   [{progress:3d}%] Phase: {phase:12s} | Status: {status}", end="\r")

            if status == "completed":
                print(f"\n   ✅ Video generation COMPLETE!")
                print(f"   📁 Output: {project.get('output_url', 'N/A')}")
                return project
            elif status == "failed":
                print(f"\n   ❌ Video generation FAILED")
                return project

            await asyncio.sleep(5)

        print("\n   ⏱️  Timeout - check status manually")
        return project


async def download_video(project_id: str, title: str):
    """Download the final video."""
    print("\n📥 Downloading final video...")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/api/v1/video/projects/{project_id}/download",
            headers=headers,
            follow_redirects=True,
        )

        if resp.status_code == 200:
            filename = f"{title.replace(' ', '_')}.mp4"
            with open(filename, "wb") as f:
                f.write(resp.content)
            print(f"   ✅ Downloaded: {filename} ({len(resp.content):,} bytes)")
        else:
            print(f"   ❌ Download failed: {resp.status_code}")


async def main():
    """Run complete video creation workflow."""
    print("=" * 60)
    print("🎬 AI Workforce OS - REAL Video Generation Demo")
    print("=" * 60)
    print(f"\nBackend: {BASE_URL}")
    print("Services: DALL-E 3 (images) + OpenAI TTS (audio) + ffmpeg (video)")
    print()

    try:
        # Step 1: Create project
        project_id = await create_project()

        # Steps 2-5: Run pipeline
        await run_pipeline(project_id)

        # Monitor progress
        project = await monitor_progress(project_id)

        # Download if completed
        if project.get("status") == "completed":
            await download_video(project_id, project["title"])

        print("\n" + "=" * 60)
        print("🎉 Done! Check your video file.")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
