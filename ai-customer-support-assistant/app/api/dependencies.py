"""
API dependencies for dependency injection.
"""

from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.repositories.query_repository import QueryRepository
from app.db.session import get_db


def get_query_repository(db: Session = Depends(get_db)) -> QueryRepository:
    """
    Dependency to get QueryRepository instance.
    
    Args:
        db: Database session (injected)
        
    Returns:
        QueryRepository instance
    """
    return QueryRepository(db)