from fastapi import APIRouter, HTTPException, status
from app.models import LoginRequest, TokenResponse, RefreshTokenRequest, PlayerCreate, PlayerResponse
from app.auth import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_token
from app.database import db
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    player = None
    for p in db.players.values():
        if p["username"] == credentials.username:
            player = p
            break
    
    if not player or not verify_password(credentials.password, player["password"]):
        logger.warning(f"Failed login attempt for username: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    player["last_login"] = datetime.utcnow()
    
    access_token = create_access_token(data={"sub": player["username"], "uuid": player["uuid"]})
    refresh_token = create_refresh_token(data={"sub": player["username"], "uuid": player["uuid"]})
    
    logger.info(f"Successful login for user: {credentials.username}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    payload = verify_token(request.refresh_token, "refresh")
    username = payload.get("sub")
    uuid = payload.get("uuid")
    
    if not username or not uuid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    access_token = create_access_token(data={"sub": username, "uuid": uuid})
    refresh_token = create_refresh_token(data={"sub": username, "uuid": uuid})
    
    logger.info(f"Token refreshed for user: {username}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/register", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def register(player_data: PlayerCreate):
    if player_data.uuid in db.players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player with this UUID already exists"
        )
    
    for p in db.players.values():
        if p["username"] == player_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    new_player = {
        "uuid": player_data.uuid,
        "username": player_data.username,
        "password": get_password_hash(player_data.password),
        "role": player_data.role,
        "inventory": {},
        "balance": 100.0,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    db.players[player_data.uuid] = new_player
    logger.info(f"New player registered: {player_data.username} ({player_data.uuid})")
    
    return PlayerResponse(
        uuid=new_player["uuid"],
        username=new_player["username"],
        role=new_player["role"],
        inventory=new_player["inventory"],
        balance=new_player["balance"],
        created_at=new_player["created_at"],
        last_login=new_player["last_login"]
    )
