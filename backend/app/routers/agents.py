"""
Agents Router - API endpoints for AI agent management
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from app.core.schemas import (
    AgentInfo,
    AgentStatus,
    AgentTask,
    SceneRequest,
    SceneResponse,
    CharacterInfo,
    WorldInfo,
    EpisodeInfo,
)

logger = logging.getLogger("ai_workforce.routers.agents")

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


@router.get("/", response_model=List[AgentInfo])
async def list_agents():
    """List all available AI agents."""
    agents = [
        AgentInfo(
            agent_id="director_ai",
            name="DirectorAI",
            role="Director AI - Manages scene creation and character direction",
            status=AgentStatus.ACTIVE,
            description="AI Director for cinematic scene generation",
            capabilities=["scene_creation", "character_management", "prompt_engineering"],
        ),
    ]
    return agents


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    """Get details of a specific agent."""
    if agent_id == "director_ai":
        return AgentInfo(
            agent_id="director_ai",
            name="DirectorAI",
            role="Director AI",
            status=AgentStatus.ACTIVE,
            description="AI Director for cinematic scene generation",
            capabilities=["scene_creation", "character_management", "prompt_engineering"],
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
        )
    raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")


@router.post("/{agent_id}/tasks", response_model=AgentTask)
async def assign_task(agent_id: str, task: AgentTask):
    """Assign a task to an agent."""
    logger.info(f"Task assigned to {agent_id}: {task.task_type}")
    task.agent_id = agent_id
    return task


# Director AI specific endpoints

director_router = APIRouter(prefix="/api/v1/agents/director", tags=["Director AI"])


@director_router.post("/scene", response_model=SceneResponse)
async def create_scene(request: SceneRequest):
    """Create a cinematic scene using DirectorAI."""
    try:
        from app.agents.director_ai.director import DirectorAI

        director = DirectorAI()
        result = director.create_scene()

        return SceneResponse(
            episode=result.get("episode", ""),
            scene=result.get("scene", ""),
            prompt=result.get("prompt", ""),
        )
    except FileNotFoundError as e:
        logger.error(f"Knowledge base file not found: {e}")
        raise HTTPException(status_code=404, detail="Knowledge base file not found")
    except Exception as e:
        logger.error(f"Scene creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scene creation failed: {str(e)}")


@director_router.get("/characters/{character_name}", response_model=CharacterInfo)
async def get_character(character_name: str):
    """Get character information from knowledge base."""
    try:
        from app.agents.director_ai.memory_loader import DirectorMemoryLoader

        loader = DirectorMemoryLoader()
        character = loader.load_character(character_name)
        return CharacterInfo(**character)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")


@director_router.get("/worlds/{world_name}", response_model=WorldInfo)
async def get_world(world_name: str):
    """Get world information from knowledge base."""
    try:
        from app.agents.director_ai.memory_loader import DirectorMemoryLoader

        loader = DirectorMemoryLoader()
        world = loader.load_world(world_name)
        return WorldInfo(**world)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"World '{world_name}' not found")


@director_router.get("/episodes/{episode_name}", response_model=EpisodeInfo)
async def get_episode(episode_name: str):
    """Get episode information from knowledge base."""
    try:
        from app.agents.director_ai.memory_loader import DirectorMemoryLoader

        loader = DirectorMemoryLoader()
        episode = loader.load_episode(episode_name)
        return EpisodeInfo(**episode)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Episode '{episode_name}' not found")
