"""
History endpoint - placeholder for Step 6.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class HistoryEntry(BaseModel):
    """Model for a single history entry."""
    id: int
    question: str
    answer: str
    timestamp: str


class HistoryResponse(BaseModel):
    """Response model for history endpoint."""
    entries: List[HistoryEntry]
    count: int
    total: int


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    n: Optional[int] = Query(10, description="Number of entries to return", ge=1, le=100)
):
    """
    Retrieve the last N questions and answers.
    
    This is a placeholder - will be fully implemented in Step 6.
    """
    logger.info(f"History requested with n={n}")
    
    # Placeholder response
    raise HTTPException(
        status_code=501,
        detail="History endpoint not implemented yet. Will be completed in Step 6."
    )