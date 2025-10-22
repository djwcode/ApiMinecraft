from fastapi import APIRouter, HTTPException, status, Depends
from app.models import TransactionRequest, TransactionResponse, BalanceResponse
from app.auth import get_current_user
from app.database import db
from datetime import datetime
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionRequest,
    current_user: str = Depends(get_current_user)
):
    if transaction_data.player_uuid not in db.players:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    player = db.players[transaction_data.player_uuid]
    
    if player["balance"] + transaction_data.amount < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    player["balance"] += transaction_data.amount
    
    transaction = {
        "id": str(uuid.uuid4()),
        "player_uuid": transaction_data.player_uuid,
        "amount": transaction_data.amount,
        "item_id": transaction_data.item_id,
        "description": transaction_data.description,
        "timestamp": datetime.utcnow(),
        "new_balance": player["balance"]
    }
    
    db.transactions.append(transaction)
    logger.info(f"Transaction created: {transaction['id']} for player {transaction_data.player_uuid}, amount: {transaction_data.amount}")
    
    return TransactionResponse(**transaction)

@router.get("/balance/{uuid}", response_model=BalanceResponse)
async def get_balance(uuid: str):
    if uuid not in db.players:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    player = db.players[uuid]
    return BalanceResponse(
        uuid=player["uuid"],
        username=player["username"],
        balance=player["balance"]
    )
