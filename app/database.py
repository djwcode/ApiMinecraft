from datetime import datetime
from typing import Dict, List, Optional
import uuid

class InMemoryDatabase:
    def __init__(self):
        self.players: Dict[str, dict] = {}
        self.quests: Dict[str, dict] = {}
        self.transactions: List[dict] = []
        self.events: Dict[str, dict] = {}
        self.player_quests: Dict[str, List[str]] = {}
        self.event_participants: Dict[str, List[str]] = {}
        self.server_start_time = datetime.utcnow()
        
        self._init_demo_data()
    
    def _init_demo_data(self):
        from app.auth import get_password_hash
        
        demo_player = {
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "username": "admin",
            "password": get_password_hash("admin123"),
            "role": "warrior",
            "inventory": {
                "sword": 1,
                "health_potion": 5,
                "gold_ore": 10
            },
            "balance": 1000.0,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        self.players[demo_player["uuid"]] = demo_player
        
        demo_quest = {
            "id": str(uuid.uuid4()),
            "title": "Defeat the Shadow Beast",
            "description": "Hunt down and defeat the Shadow Beast terrorizing the northern villages",
            "status": "available",
            "reward": 500.0,
            "objectives": [
                "Find the Shadow Beast lair",
                "Defeat 10 shadow minions",
                "Defeat the Shadow Beast"
            ],
            "progress": 0,
            "created_at": datetime.utcnow()
        }
        self.quests[demo_quest["id"]] = demo_quest
        
        demo_event = {
            "id": str(uuid.uuid4()),
            "event_type": "boss_raid",
            "zone": "Dark Forest",
            "difficulty": 7,
            "reward_multiplier": 2.0,
            "active": True,
            "created_at": datetime.utcnow(),
            "participants": []
        }
        self.events[demo_event["id"]] = demo_event

db = InMemoryDatabase()
