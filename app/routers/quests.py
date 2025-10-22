from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models import QuestResponse, QuestCreate, QuestProgress, QuestStatus
from app.auth import get_current_user
from app.database import db
from typing import List, Optional
import uuid
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=List[QuestResponse])
async def get_quests(
    status_filter: Optional[QuestStatus] = Query(None, alias="status", description="Filter quests by status"),
    limit: int = Query(20, ge=1, le=100)
):
    quests = list(db.quests.values())
    
    if status_filter:
        quests = [q for q in quests if q["status"] == status_filter]
    
    quests = quests[:limit]
    
    return [
        QuestResponse(
            id=q["id"],
            title=q["title"],
            description=q["description"],
            status=q["status"],
            reward=q["reward"],
            objectives=q["objectives"],
            progress=q["progress"],
            created_at=q["created_at"]
        )
        for q in quests
    ]

@router.get("/{quest_id}", response_model=QuestResponse)
async def get_quest(quest_id: str):
    if quest_id not in db.quests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quest not found"
        )
    
    quest = db.quests[quest_id]
    return QuestResponse(
        id=quest["id"],
        title=quest["title"],
        description=quest["description"],
        status=quest["status"],
        reward=quest["reward"],
        objectives=quest["objectives"],
        progress=quest["progress"],
        created_at=quest["created_at"]
    )

@router.post("", response_model=QuestResponse, status_code=status.HTTP_201_CREATED)
async def create_quest(
    quest_data: QuestCreate,
    current_user: str = Depends(get_current_user)
):
    quest_id = str(uuid.uuid4())
    
    new_quest = {
        "id": quest_id,
        "title": quest_data.title,
        "description": quest_data.description,
        "status": "available",
        "reward": quest_data.reward,
        "objectives": quest_data.objectives,
        "progress": 0,
        "created_at": datetime.utcnow()
    }
    
    db.quests[quest_id] = new_quest
    logger.info(f"New quest created: {quest_data.title} ({quest_id})")
    
    return QuestResponse(**new_quest)

@router.patch("/{quest_id}/progress", response_model=QuestResponse)
async def update_quest_progress(
    quest_id: str,
    progress_data: QuestProgress,
    current_user: str = Depends(get_current_user)
):
    if quest_id not in db.quests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quest not found"
        )
    
    quest = db.quests[quest_id]
    quest["progress"] = progress_data.progress
    
    if progress_data.progress >= 100:
        quest["status"] = "completed"
        
        if progress_data.player_uuid in db.players:
            player = db.players[progress_data.player_uuid]
            player["balance"] += quest["reward"]
            logger.info(f"Quest {quest_id} completed by {progress_data.player_uuid}. Reward {quest['reward']} added.")
    
    logger.info(f"Quest {quest_id} progress updated to {progress_data.progress}%")
    
    return QuestResponse(**quest)
