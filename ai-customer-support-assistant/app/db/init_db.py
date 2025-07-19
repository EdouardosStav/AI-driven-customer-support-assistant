"""
Database initialization module.
"""

from pathlib import Path

from sqlalchemy import inspect

from app.core.logging import get_logger

logger = get_logger(__name__)


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This function creates all tables defined in the models
    if they don't already exist.
    """
    # Import here to avoid circular imports
    from app.db.base import Base
    from app.db.session import engine
    # Import models to register them
    from app.models import query_log  # noqa: F401
    
    try:
        # Get the database URL
        db_url = str(engine.url)
        logger.info(f"Initializing database at: {db_url}")
        
        # For SQLite, ensure the directory exists
        if "sqlite" in db_url:
            # Extract the file path from the URL
            if ":///" in db_url:
                db_path = db_url.split(":///")[-1]
            else:
                db_path = "customer_support.db"
            
            db_path = Path(db_path)
            logger.info(f"SQLite database path: {db_path.absolute()}")
            
            # Create directory if it doesn't exist
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if tables already exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            logger.info(f"Found existing tables: {existing_tables}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Database initialized successfully with tables: {tables}")
        
        # Log table details
        for table in tables:
            columns = [col['name'] for col in inspector.get_columns(table)]
            logger.debug(f"Table '{table}' columns: {columns}")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def drop_all_tables() -> None:
    """
    Drop all tables in the database.
    
    WARNING: This will delete all data!
    Use only for development/testing.
    """
    from app.db.base import Base
    from app.db.session import engine
    
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped successfully")


def reset_database() -> None:
    """
    Reset the database by dropping and recreating all tables.
    
    WARNING: This will delete all data!
    Use only for development/testing.
    """
    logger.warning("Resetting database...")
    drop_all_tables()
    init_db()
    logger.info("Database reset complete")