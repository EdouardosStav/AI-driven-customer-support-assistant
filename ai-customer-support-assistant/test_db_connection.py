"""
Simple test to debug database connection issues.
"""

import os
from pathlib import Path

# Add the app directory to the Python path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

print("Database Configuration Debug")
print("=" * 50)
print(f"DATABASE_URL from env: {settings.database_url}")
print(f"Processed URL: {settings.get_database_url()}")
print(f"Current working directory: {os.getcwd()}")
print(f"Absolute DB path: {os.path.abspath('customer_support.db')}")

# Test creating the database file manually
db_path = Path("customer_support.db")
print(f"\nTrying to create database at: {db_path.absolute()}")

try:
    # Try to create an empty file
    db_path.touch()
    print("✅ Successfully created database file")
    
    # Now test SQLAlchemy connection
    from sqlalchemy import create_engine, text
    
    engine = create_engine(settings.get_database_url(), echo=True)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"✅ Database connection successful! Result: {result.scalar()}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()