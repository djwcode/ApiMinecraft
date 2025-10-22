from fastapi import APIRouter, Depends
from app.models import StatsResponse
from app.auth import require_admin
from app.database import db
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/stats", response_model=StatsResponse)
async def get_stats(current_user: str = Depends(require_admin)):
    online_count = sum(1 for p in db.players.values() if p.get("last_login") and 
                       (datetime.utcnow() - p["last_login"]).total_seconds() < 3600)
    
    active_quests = sum(1 for q in db.quests.values() if q["status"] == "active")
    active_events = sum(1 for e in db.events.values() if e["active"])
    
    uptime = datetime.utcnow() - db.server_start_time
    uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
    
    return StatsResponse(
        total_players=len(db.players),
        online_players=online_count,
        active_quests=active_quests,
        active_events=active_events,
        total_transactions=len(db.transactions),
        server_uptime=uptime_str
    )
