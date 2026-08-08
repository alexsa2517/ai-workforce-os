"""
Agents Router - Database-backed AI agent management
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from app.core.schemas import AgentInfo, AgentCreate, AgentUpdate, TaskInfo, TaskCreate, AgentStatus, TaskStatus
from app.middleware.error_handler import APIError
from app.database.session import get_db
from app.database.models import AIAgent, AITask
from app.services.monitoring import metrics

logger = logging.getLogger("ai_workforce.routers.agents")

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


@router.get("/", response_model=List[AgentInfo])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    status: Optional[AgentStatus] = None,
    skip: int = 0,
    limit: int = 100,
):
    """List all registered AI agents with optional filtering."""
    query = select(AIAgent).offset(skip).limit(limit)

    if status:
        query = query.where(AIAgent.status == status.value)

    result = await db.execute(query)
    agents = result.scalars().all()

    # Update metrics
    for s in AgentStatus:
        count = len([a for a in agents if a.status == s.value])
        metrics.set_agent_count(s.value, count)

    return [
        AgentInfo(
            agent_id=a.agent_id,
            name=a.name,
            role=a.role,
            status=AgentStatus(a.status),
            description=a.description,
            capabilities=a.capabilities or [],
            config=a.config,
            created_at=a.created_at,
            updated_at=a.updated_at,
            last_active=a.last_active,
        )
        for a in agents
    ]


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get details of a specific agent."""
    result = await db.execute(select(AIAgent).where(AIAgent.agent_id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise APIError(
            message=f"Agent '{agent_id}' not found",
            status_code=404,
            error_code="agent_not_found",
        )

    return AgentInfo(
        agent_id=agent.agent_id,
        name=agent.name,
        role=agent.role,
        status=AgentStatus(agent.status),
        description=agent.description,
        capabilities=agent.capabilities or [],
        config=agent.config,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        last_active=agent.last_active,
    )


@router.post("/", response_model=AgentInfo, status_code=201)
async def create_agent(agent: AgentCreate, db: AsyncSession = Depends(get_db)):
    """Register a new AI agent."""
    # Check if agent_id already exists
    result = await db.execute(select(AIAgent).where(AIAgent.agent_id == agent.agent_id))
    if result.scalar_one_or_none():
        raise APIError(
            message=f"Agent '{agent.agent_id}' already exists",
            status_code=409,
            error_code="agent_exists",
        )

    new_agent = AIAgent(
        agent_id=agent.agent_id,
        name=agent.name,
        role=agent.role,
        description=agent.description,
        status=AgentStatus.IDLE.value,
        capabilities=agent.capabilities,
        config=agent.config,
        last_active=datetime.now(timezone.utc),
    )

    db.add(new_agent)
    await db.commit()
    await db.refresh(new_agent)

    logger.info(f"Agent created: {agent.agent_id}")

    return AgentInfo(
        agent_id=new_agent.agent_id,
        name=new_agent.name,
        role=new_agent.role,
        status=AgentStatus(new_agent.status),
        description=new_agent.description,
        capabilities=new_agent.capabilities or [],
        config=new_agent.config,
        created_at=new_agent.created_at,
        last_active=new_agent.last_active,
    )


@router.put("/{agent_id}", response_model=AgentInfo)
async def update_agent(agent_id: str, update: AgentUpdate, db: AsyncSession = Depends(get_db)):
    """Update an existing agent."""
    result = await db.execute(select(AIAgent).where(AIAgent.agent_id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise APIError(
            message=f"Agent '{agent_id}' not found",
            status_code=404,
            error_code="agent_not_found",
        )

    update_data = update.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value

    update_data["updated_at"] = datetime.now(timezone.utc)

    await db.execute(
        update(AIAgent)
        .where(AIAgent.agent_id == agent_id)
        .values(**update_data)
    )
    await db.commit()

    # Refresh and return
    result = await db.execute(select(AIAgent).where(AIAgent.agent_id == agent_id))
    agent = result.scalar_one()

    logger.info(f"Agent updated: {agent_id}")

    return AgentInfo(
        agent_id=agent.agent_id,
        name=agent.name,
        role=agent.role,
        status=AgentStatus(agent.status),
        description=agent.description,
        capabilities=agent.capabilities or [],
        config=agent.config,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        last_active=agent.last_active,
    )


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an agent and all associated data."""
    result = await db.execute(select(AIAgent).where(AIAgent.agent_id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise APIError(
            message=f"Agent '{agent_id}' not found",
            status_code=404,
            error_code="agent_not_found",
        )

    await db.delete(agent)
    await db.commit()

    logger.info(f"Agent deleted: {agent_id}")
    return None


# Task endpoints
@router.get("/{agent_id}/tasks", response_model=List[TaskInfo])
async def list_agent_tasks(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    status: Optional[TaskStatus] = None,
    skip: int = 0,
    limit: int = 50,
):
    """List tasks for a specific agent."""
    query = select(AITask).where(AITask.agent_id == agent_id).offset(skip).limit(limit)

    if status:
        query = query.where(AITask.status == status.value)

    result = await db.execute(query.order_by(AITask.created_at.desc()))
    tasks = result.scalars().all()

    return [
        TaskInfo(
            task_id=t.task_id,
            agent_id=t.agent_id,
            task_type=t.task_type,
            description=t.description,
            priority=t.priority,
            status=TaskStatus(t.status),
            parameters=t.parameters,
            result=t.result,
            error_message=t.error_message,
            created_at=t.created_at,
            started_at=t.started_at,
            completed_at=t.completed_at,
        )
        for t in tasks
    ]


@router.post("/{agent_id}/tasks", response_model=TaskInfo, status_code=201)
async def create_task(agent_id: str, task: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a new task for an agent."""
    # Verify agent exists
    result = await db.execute(select(AIAgent).where(AIAgent.agent_id == agent_id))
    if not result.scalar_one_or_none():
        raise APIError(
            message=f"Agent '{agent_id}' not found",
            status_code=404,
            error_code="agent_not_found",
        )

    new_task = AITask(
        task_id=task.task_id,
        agent_id=task.agent_id,
        task_type=task.task_type,
        description=task.description,
        priority=task.priority,
        status=TaskStatus.PENDING.value,
        parameters=task.parameters,
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    logger.info(f"Task created: {task.task_id} for agent {agent_id}")

    return TaskInfo(
        task_id=new_task.task_id,
        agent_id=new_task.agent_id,
        task_type=new_task.task_type,
        description=new_task.description,
        priority=new_task.priority,
        status=TaskStatus(new_task.status),
        parameters=new_task.parameters,
        created_at=new_task.created_at,
    )
