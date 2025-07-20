"""
History endpoint - Retrieve past questions and answers.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.api.dependencies import get_query_repository
from app.core.logging import get_logger
from app.db.repositories.query_repository import QueryRepository

logger = get_logger(__name__)

router = APIRouter()


class HistoryEntry(BaseModel):
    """Model for a single history entry."""
    id: int = Field(..., description="Unique identifier")
    question: str = Field(..., description="User's question")
    answer: str = Field(..., description="AI-generated answer")
    timestamp: str = Field(..., description="ISO format timestamp")
    processing_time: Optional[int] = Field(None, description="Processing time in milliseconds")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "question": "What is the refund policy?",
                "answer": "Our refund policy allows...",
                "timestamp": "2024-01-20T10:30:00Z",
                "processing_time": 1250
            }
        }


class HistoryResponse(BaseModel):
    """Response model for history endpoint."""
    entries: List[HistoryEntry] = Field(..., description="List of Q&A entries")
    count: int = Field(..., description="Number of entries returned")
    total: int = Field(..., description="Total entries in database")
    
    class Config:
        schema_extra = {
            "example": {
                "entries": [
                    {
                        "id": 123,
                        "question": "What is the refund policy?",
                        "answer": "Our refund policy allows...",
                        "timestamp": "2024-01-20T10:30:00Z",
                        "processing_time": 1250
                    }
                ],
                "count": 1,
                "total": 150
            }
        }


@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="Get question history",
    description="Retrieve the last N questions and answers with timestamps"
)
async def get_history(
    n: Optional[int] = Query(
        10,
        description="Number of entries to return",
        ge=1,
        le=100,
        alias="n"
    ),
    search: Optional[str] = Query(
        None,
        description="Search term to filter questions",
        min_length=2,
        max_length=100
    ),
    query_repo: QueryRepository = Depends(get_query_repository)
):
    """
    Retrieve the last N questions and answers.
    
    This endpoint returns recent Q&A pairs stored in the database,
    ordered by timestamp (most recent first).
    
    Args:
        n: Number of entries to return (1-100, default: 10)
        search: Optional search term to filter questions
        query_repo: Database repository (injected)
        
    Returns:
        HistoryResponse with list of entries and metadata
        
    Raises:
        HTTPException: On database errors
    """
    logger.info(f"History requested with n={n}, search={search}")
    
    try:
        # Get entries based on search term
        if search:
            # Search by question content
            entries = query_repo.search_by_question(search_term=search, limit=n)
            logger.info(f"Found {len(entries)} entries matching '{search}'")
        else:
            # Get latest entries
            entries = query_repo.get_latest(limit=n)
        
        # Get total count
        total_count = query_repo.count()
        
        # Convert to response format
        history_entries = []
        for entry in entries:
            history_entries.append(
                HistoryEntry(
                    id=entry.id,
                    question=entry.question,
                    answer=entry.answer,
                    timestamp=entry.timestamp.isoformat() + "Z",
                    processing_time=entry.processing_time
                )
            )
        
        return HistoryResponse(
            entries=history_entries,
            count=len(history_entries),
            total=total_count
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve history. Please try again."
        )