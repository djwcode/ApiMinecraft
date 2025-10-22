from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from app.routers import auth, players, quests, economy, events, admin

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="Minecraft RP-PVE Server API",
    description="RESTful API for Minecraft server with authentication, quests, economy, and PVE events",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(players.router, prefix="/api/v1/players", tags=["Players"])
app.include_router(quests.router, prefix="/api/v1/quests", tags=["Quests"])
app.include_router(economy.router, prefix="/api/v1/economy", tags=["Economy"])
app.include_router(events.router, prefix="/api/v1/events", tags=["PVE Events"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {
        "message": "Minecraft RP-PVE Server API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

logger.info("API initialized successfully")
