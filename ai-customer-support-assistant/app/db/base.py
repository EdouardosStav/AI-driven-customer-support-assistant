"""
Database base configuration with SQLAlchemy.
"""

try:
    # SQLAlchemy 2.x
    from sqlalchemy.orm import declarative_base
except ImportError:
    # SQLAlchemy 1.x fallback
    from sqlalchemy.ext.declarative import declarative_base

# Create the declarative base for all models
Base = declarative_base()

# Import all models here to ensure they're registered with Base
# This is important for Alembic migrations
# Note: This import is placed at the end to avoid circular imports