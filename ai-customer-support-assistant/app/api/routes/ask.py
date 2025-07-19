"""
Ask endpoint - placeholder for Step 5.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class AskRequest(BaseModel):
    """Request model for ask endpoint."""
    question: str


class AskResponse(BaseModel):
    """Response model for ask endpoint."""
    answer: str
    question_id: int
    timestamp: str


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Process a user question and return an AI-generated answer.
    
    This is a placeholder - will be fully implemented in Step 5.
    """
    logger.info(f"Received question: {request.question}")
    
    # Placeholder response
    raise HTTPException(
        status_code=501,
        detail="Ask endpoint not implemented yet. Will be completed in Step 5."
    )