"""
Ask endpoint - Process user questions and return AI-generated answers.
"""

import time
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, validator

from app.api.dependencies import get_query_repository
from app.core.exceptions import LLMException, OllamaConnectionException
from app.core.logging import get_logger
from app.db.repositories.query_repository import QueryRepository
from app.services.llm_wrapper import CustomerSupportLLM

logger = get_logger(__name__)

router = APIRouter()


class AskRequest(BaseModel):
    """Request model for ask endpoint."""
    question: str = Field(
        ..., 
        min_length=3, 
        max_length=500,
        description="The customer's question"
    )
    context_method: Optional[str] = Field(
        "keyword",
        description="Context selection method: 'all' or 'keyword'"
    )
    
    @validator('question')
    def validate_question(cls, v):
        """Validate and clean the question."""
        # Strip whitespace
        v = v.strip()
        
        # Check if it's not just punctuation
        if not any(c.isalnum() for c in v):
            raise ValueError("Question must contain at least some text")
        
        return v
    
    @validator('context_method')
    def validate_context_method(cls, v):
        """Validate context method."""
        valid_methods = ["all", "keyword"]
        if v not in valid_methods:
            raise ValueError(f"Context method must be one of: {valid_methods}")
        return v


class AskResponse(BaseModel):
    """Response model for ask endpoint."""
    answer: str = Field(..., description="AI-generated answer")
    question_id: int = Field(..., description="ID of the stored question")
    timestamp: str = Field(..., description="ISO format timestamp")
    processing_time: int = Field(..., description="Processing time in milliseconds")
    
    class Config:
        schema_extra = {
            "example": {
                "answer": "Our refund policy allows returns within 30 days...",
                "question_id": 123,
                "timestamp": "2024-01-20T10:30:00Z",
                "processing_time": 1250
            }
        }


@router.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask a customer support question",
    description="Submit a question and receive an AI-generated answer based on the knowledge base"
)
async def ask_question(
    request: AskRequest,
    req: Request,
    query_repo: QueryRepository = Depends(get_query_repository)
):
    """
    Process a user question and return an AI-generated answer.
    
    This endpoint:
    1. Validates the input question
    2. Uses the LLM to generate an answer based on the knowledge base
    3. Stores the Q&A pair in the database
    4. Returns the answer with metadata
    
    Args:
        request: The ask request containing the question
        req: FastAPI request object for accessing app state
        query_repo: Database repository (injected)
        
    Returns:
        AskResponse with answer and metadata
        
    Raises:
        HTTPException: On validation errors or processing failures
    """
    logger.info(
        f"Received question: {request.question[:50]}...",
        extra={"request_id": getattr(req.state, "request_id", None)}
    )
    
    start_time = time.time()
    
    try:
        # Get LLM from app state (initialized in main.py)
        if not hasattr(req.app.state, "knowledge_base") or req.app.state.knowledge_base is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Knowledge base not loaded. Please try again later."
            )
        
        # Initialize LLM with knowledge base
        llm = CustomerSupportLLM(knowledge_base=req.app.state.knowledge_base)
        
        try:
            # Generate answer
            llm_result = llm.answer_question(
                question=request.question,
                context_method=request.context_method,
                temperature=0.3,  # Lower temperature for consistent answers
                max_tokens=300
            )
            
            # Extract answer and metadata
            answer = llm_result["answer"]
            model_used = llm_result["model_used"]
            context_length = llm_result["context_length"]
            
        finally:
            llm.close()
        
        # Calculate total processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Store in database
        try:
            query_log = query_repo.create(
                question=request.question,
                answer=answer,
                processing_time=processing_time,
                model_used=model_used,
                context_used=f"Method: {request.context_method}, Length: {context_length}"
            )
            
            logger.info(
                f"Successfully processed question. ID: {query_log.id}, Time: {processing_time}ms",
                extra={"request_id": getattr(req.state, "request_id", None)}
            )
            
            # Return response
            return AskResponse(
                answer=answer,
                question_id=query_log.id,
                timestamp=query_log.timestamp.isoformat() + "Z",
                processing_time=processing_time
            )
            
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            # Still return the answer even if DB storage fails
            return AskResponse(
                answer=answer,
                question_id=0,  # Indicate DB storage failed
                timestamp=datetime.utcnow().isoformat() + "Z",
                processing_time=processing_time
            )
    
    except OllamaConnectionException as e:
        logger.error(f"Ollama connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is currently unavailable. Please ensure Ollama is running."
        )
    
    except LLMException as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate answer: {str(e)}"
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error in ask endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )