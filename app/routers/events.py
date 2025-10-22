from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models import EventResponse, EventCreate
from app.auth import get_current_user
from app.database import db
from typing import List
import uuid
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=List[EventResponse])
async def get_events(
    active_only: bool = Query(True, description="Show only active events"),
    limit: int = Query(20, ge=1, le=100)
):
    events = list(db.events.values())
    
    if active_only:
        events = [e for e in events if e["active"]]
    
    events = events[:limit]
    
    return [
        EventResponse(
            id=e["id"],
            event_type=e["event_type"],
            zone=e["zone"],
            difficulty=e["difficulty"],
            reward_multiplier=e["reward_multiplier"],
            active=e["active"],
            created_at=e["created_at"],
            participants=db.event_participants.get(e["id"], [])
        )
        for e in events
    ]

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    if event_id not in db.events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    event = db.events[event_id]
    return EventResponse(
        id=event["id"],
        event_type=event["event_type"],
        zone=event["zone"],
        difficulty=event["difficulty"],
        reward_multiplier=event["reward_multiplier"],
        active=event["active"],
        created_at=event["created_at"],
        participants=db.event_participants.get(event_id, [])
    )

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: str = Depends(get_current_user)
):
    event_id = str(uuid.uuid4())
    
    new_event = {
        "id": event_id,
        "event_type": event_data.event_type,
        "zone": event_data.zone,
        "difficulty": event_data.difficulty,
        "reward_multiplier": event_data.reward_multiplier,
        "active": True,
        "created_at": datetime.utcnow()
    }
    
    db.events[event_id] = new_event
    db.event_participants[event_id] = []
    
    logger.info(f"New event created: {event_data.event_type} in {event_data.zone} ({event_id})")
    
    return EventResponse(
        id=new_event["id"],
        event_type=new_event["event_type"],
        zone=new_event["zone"],
        difficulty=new_event["difficulty"],
        reward_multiplier=new_event["reward_multiplier"],
        active=new_event["active"],
        created_at=new_event["created_at"],
        participants=[]
    )

@router.post("/{event_id}/join")
async def join_event(
    event_id: str,
    player_uuid: str = Query(..., description="Player UUID"),
    current_user: str = Depends(get_current_user)
):
    if event_id not in db.events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if player_uuid not in db.players:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    event = db.events[event_id]
    if not event["active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not active"
        )
    
    if event_id not in db.event_participants:
        db.event_participants[event_id] = []
    
    if player_uuid not in db.event_participants[event_id]:
        db.event_participants[event_id].append(player_uuid)
        logger.info(f"Player {player_uuid} joined event {event_id}")
    
    return {"message": "Successfully joined event", "event_id": event_id}

@router.post("/{event_id}/end")
async def end_event(
    event_id: str,
    current_user: str = Depends(get_current_user)
):
    if event_id not in db.events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.events[event_id]["active"] = False
    logger.info(f"Event {event_id} ended")
    
    return {"message": "Event ended successfully", "event_id": event_id}
