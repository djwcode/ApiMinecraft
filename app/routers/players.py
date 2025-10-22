from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models import PlayerResponse, PlayerUpdate, PlayerRole
from app.auth import get_current_user
from app.database import db
from typing import List, Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=List[PlayerResponse])
async def get_players(
    role: Optional[PlayerRole] = Query(None, description="Filter players by role"),
    limit: int = Query(20, ge=1, le=100)
):
    players = list(db.players.values())
    
    if role:
        players = [p for p in players if p["role"] == role]
    
    players = players[:limit]
    
    return [
        PlayerResponse(
            uuid=p["uuid"],
            username=p["username"],
            role=p["role"],
            inventory=p["inventory"],
            balance=p["balance"],
            created_at=p["created_at"],
            last_login=p["last_login"]
        )
        for p in players
    ]

@router.get("/{uuid}", response_model=PlayerResponse)
async def get_player(uuid: str):
    if uuid not in db.players:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    player = db.players[uuid]
    return PlayerResponse(
        uuid=player["uuid"],
        username=player["username"],
        role=player["role"],
        inventory=player["inventory"],
        balance=player["balance"],
        created_at=player["created_at"],
        last_login=player["last_login"]
    )

@router.put("/{uuid}", response_model=PlayerResponse)
async def update_player(
    uuid: str,
    update_data: PlayerUpdate,
    current_user: str = Depends(get_current_user)
):
    if uuid not in db.players:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    player = db.players[uuid]
    
    if update_data.role is not None:
        player["role"] = update_data.role
        logger.info(f"Player {uuid} role updated to {update_data.role}")
    
    if update_data.inventory is not None:
        player["inventory"] = update_data.inventory
        logger.info(f"Player {uuid} inventory updated")
    
    return PlayerResponse(
        uuid=player["uuid"],
        username=player["username"],
        role=player["role"],
        inventory=player["inventory"],
        balance=player["balance"],
        created_at=player["created_at"],
        last_login=player["last_login"]
    )

@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(uuid: str, current_user: str = Depends(get_current_user)):
    if uuid not in db.players:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    del db.players[uuid]
    logger.info(f"Player {uuid} deleted")
    return None
