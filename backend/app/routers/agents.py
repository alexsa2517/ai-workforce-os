"""
Agents Router - API endpoints for managing AI agents
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.schemas import AgentInfo, AgentStatus, AgentTask, TaskStatus, SceneRequest, SceneResponse, CharacterInfo, WorldInfo, EpisodeInfo

logger = logging.getLogger("ai_workforce.routers.agents")

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


class AgentCreate(BaseModel):
    """Request schema for creating a new agent."""
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., min_length=1, description="Agent display name")
    role: str = Field(..., description="Agent role")
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    config: Optional[dict] = None


class AgentUpdate(BaseModel):
    """Request schema for updating an agent."""
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AgentStatus] = None
    capabilities: Optional[List[str]] = None
    config: Optional[dict] = None


# In-memory agent registry (in production, use database)
_agent_registry = {
    "director_ai": AgentInfo(
        agent_id="director_ai",
        name="DirectorAI",
        role="Director AI",
        status=AgentStatus.ACTIVE,
        description="AI Director for cinematic scene generation",
        capabilities=["scene_creation", "character_management", "prompt_engineering"],
        created_at=datetime.now(timezone.utc),
        last_active=datetime.now(timezone.utc),
    ),
    "sales_ai_001": AgentInfo(
        agent_id="sales_ai_001",
        name="Sales AI Employee #001",
        role="Sales Representative",
        status=AgentStatus.IDLE,
        description="AI-powered sales representative for customer interactions",
        capabilities=["customer_service", "lead_qualification", "sales_pitch"],
        created_at=datetime.now(timezone.utc),
        last_active=datetime.now(timezone.utc),
    ),
}


@router.get("/", response_model=List[AgentInfo])
async def list_agents():
    """List all registered AI agents."""
    return list(_agent_registry.values())


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    """Get details of a specific agent."""
    agent = _agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return agent


@router.post("/", response_model=AgentInfo)
async def create_agent(agent: AgentCreate):
    """Register a new AI agent."""
    if agent.agent_id in _agent_registry:
        raise HTTPException(
            status_code=409,
            detail=f"Agent '{agent.agent_id}' already exists",
        )
    info = AgentInfo(
        agent_id=agent.agent_id,
        name=agent.name,
        role=agent.role,
        description=agent.description,
        capabilities=agent.capabilities,
        created_at=datetime.now(timezone.utc),
        last_active=datetime.now(timezone.utc),
    )
    _agent_registry[agent.agent_id] = info
    logger.info(f"Agent created: {agent.agent_id}")
    return info


@router.patch("/{agent_id}", response_model=AgentInfo)
async def update_agent(agent_id: str, update: AgentUpdate):
    """Update an existing agent."""
    agent = _agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(agent, key, value)
    agent.last_active = datetime.now(timezone.utc)

    logger.info(f"Agent updated: {agent_id}")
    return agent


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """Remove an agent from the registry."""
    if agent_id not in _agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    del _agent_registry[agent_id]
    logger.info(f"Agent deleted: {agent_id}")
    return {"message": f"Agent '{agent_id}' deleted"}


@router.post("/{agent_id}/tasks", response_model=AgentTask)
async def assign_task(agent_id: str, task: AgentTask):
    """Assign a task to an agent."""
    if agent_id not in _agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    task.agent_id = agent_id
    task.status = TaskStatus.PENDING
    logger.info(f"Task assigned to {agent_id}: {task.task_type}")
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
