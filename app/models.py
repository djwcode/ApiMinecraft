from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PlayerRole(str, Enum):
    WARRIOR = "warrior"
    MAGE = "mage"
    ARCHER = "archer"
    HEALER = "healer"
    CRAFTER = "crafter"

class QuestStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    AVAILABLE = "available"

class EventType(str, Enum):
    MOB_SPAWN = "mob_spawn"
    BOSS_RAID = "boss_raid"
    ZONE_DEFENSE = "zone_defense"
    TREASURE_HUNT = "treasure_hunt"

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=16)
    password: str = Field(..., min_length=6)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PlayerCreate(BaseModel):
    uuid: str = Field(..., min_length=32, max_length=36)
    username: str = Field(..., min_length=3, max_length=16)
    role: PlayerRole = PlayerRole.WARRIOR
    password: str = Field(..., min_length=6)

class PlayerUpdate(BaseModel):
    role: Optional[PlayerRole] = None
    inventory: Optional[Dict[str, Any]] = None

class PlayerResponse(BaseModel):
    uuid: str
    username: str
    role: PlayerRole
    inventory: Dict[str, Any]
    balance: float
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class QuestCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=500)
    reward: float = Field(..., gt=0)
    objectives: List[str] = Field(..., min_length=1)

class QuestProgress(BaseModel):
    quest_id: str
    player_uuid: str
    progress: int = Field(..., ge=0, le=100)

class QuestResponse(BaseModel):
    id: str
    title: str
    description: str
    status: QuestStatus
    reward: float
    objectives: List[str]
    progress: int
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TransactionRequest(BaseModel):
    player_uuid: str = Field(..., min_length=32, max_length=36)
    amount: float
    item_id: Optional[str] = None
    description: str

class TransactionResponse(BaseModel):
    id: str
    player_uuid: str
    amount: float
    item_id: Optional[str]
    description: str
    timestamp: datetime
    new_balance: float

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class BalanceResponse(BaseModel):
    uuid: str
    username: str
    balance: float

class EventCreate(BaseModel):
    event_type: EventType
    zone: str = Field(..., min_length=1, max_length=50)
    difficulty: int = Field(..., ge=1, le=10)
    reward_multiplier: float = Field(default=1.0, gt=0)

class EventResponse(BaseModel):
    id: str
    event_type: EventType
    zone: str
    difficulty: int
    reward_multiplier: float
    active: bool
    created_at: datetime
    participants: List[str]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StatsResponse(BaseModel):
    total_players: int
    online_players: int
    active_quests: int
    active_events: int
    total_transactions: int
    server_uptime: str
