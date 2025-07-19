"""
Repository for QueryLog database operations.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.query_log import QueryLog

logger = get_logger(__name__)


class QueryRepository:
    """
    Repository class for QueryLog operations.
    
    Implements the repository pattern for database operations.
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create(
        self,
        question: str,
        answer: str,
        processing_time: Optional[int] = None,
        model_used: str = "mistral",
        context_used: Optional[str] = None
    ) -> QueryLog:
        """
        Create a new query log entry.
        
        Args:
            question: User's question
            answer: AI-generated answer
            processing_time: Time taken to process (milliseconds)
            model_used: LLM model used
            context_used: Knowledge base context used
            
        Returns:
            QueryLog: Created query log entry
        """
        try:
            # Calculate text lengths
            question_length = len(question)
            answer_length = len(answer)
            
            # Create new entry
            query_log = QueryLog(
                question=question,
                answer=answer,
                processing_time=processing_time,
                model_used=model_used,
                context_used=context_used,
                question_length=question_length,
                answer_length=answer_length
            )
            
            # Add to session and commit
            self.db.add(query_log)
            self.db.commit()
            self.db.refresh(query_log)
            
            logger.info(f"Created query log entry {query_log.id}")
            return query_log
            
        except Exception as e:
            logger.error(f"Failed to create query log: {e}")
            self.db.rollback()
            raise
    
    def get_by_id(self, query_id: int) -> Optional[QueryLog]:
        """
        Get a query log by ID.
        
        Args:
            query_id: ID of the query log
            
        Returns:
            QueryLog or None if not found
        """
        return self.db.query(QueryLog).filter(QueryLog.id == query_id).first()
    
    def get_latest(self, limit: int = 10) -> List[QueryLog]:
        """
        Get the latest query logs.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of QueryLog entries
        """
        return (
            self.db.query(QueryLog)
            .order_by(desc(QueryLog.timestamp))
            .limit(limit)
            .all()
        )
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[QueryLog]:
        """
        Get all query logs with pagination.
        
        Args:
            skip: Number of entries to skip
            limit: Maximum number of entries to return
            
        Returns:
            List of QueryLog entries
        """
        return (
            self.db.query(QueryLog)
            .order_by(desc(QueryLog.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count(self) -> int:
        """
        Get total count of query logs.
        
        Returns:
            Total number of entries
        """
        return self.db.query(QueryLog).count()
    
    def search_by_question(self, search_term: str, limit: int = 10) -> List[QueryLog]:
        """
        Search query logs by question content.
        
        Args:
            search_term: Term to search for
            limit: Maximum number of results
            
        Returns:
            List of matching QueryLog entries
        """
        return (
            self.db.query(QueryLog)
            .filter(QueryLog.question.ilike(f"%{search_term}%"))
            .order_by(desc(QueryLog.timestamp))
            .limit(limit)
            .all()
        )
    
    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100
    ) -> List[QueryLog]:
        """
        Get query logs within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            limit: Maximum number of results
            
        Returns:
            List of QueryLog entries
        """
        return (
            self.db.query(QueryLog)
            .filter(QueryLog.timestamp >= start_date)
            .filter(QueryLog.timestamp <= end_date)
            .order_by(desc(QueryLog.timestamp))
            .limit(limit)
            .all()
        )
    
    def get_average_processing_time(self) -> Optional[float]:
        """
        Get average processing time for all queries.
        
        Returns:
            Average processing time in milliseconds
        """
        from sqlalchemy import func
        
        result = self.db.query(
            func.avg(QueryLog.processing_time)
        ).filter(
            QueryLog.processing_time.isnot(None)
        ).scalar()
        
        return float(result) if result else None