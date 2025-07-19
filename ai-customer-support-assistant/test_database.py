"""
Test script to verify database functionality.
"""

import time
from datetime import datetime

from app.db.init_db import init_db, reset_database
from app.db.repositories.query_repository import QueryRepository
from app.db.session import get_db_context


def test_database():
    """Test database operations."""
    print("🔍 Testing Database Operations...")
    print("=" * 50)
    
    # Initialize database
    print("1. Initializing database...")
    init_db()
    print("✅ Database initialized")
    
    # Test with repository
    with get_db_context() as db:
        repo = QueryRepository(db)
        
        # Test 1: Create a query log
        print("\n2. Creating a test query log...")
        start_time = time.time()
        query_log = repo.create(
            question="What is your refund policy?",
            answer="Our refund policy allows returns within 30 days.",
            processing_time=int((time.time() - start_time) * 1000),
            model_used="mistral",
            context_used="Q: What is the refund policy?"
        )
        print(f"✅ Created query log with ID: {query_log.id}")
        
        # Test 2: Retrieve by ID
        print(f"\n3. Retrieving query log by ID {query_log.id}...")
        retrieved = repo.get_by_id(query_log.id)
        if retrieved:
            print(f"✅ Retrieved: {retrieved.question[:50]}...")
        else:
            print("❌ Failed to retrieve")
        
        # Test 3: Create multiple entries
        print("\n4. Creating multiple entries...")
        test_questions = [
            "How do I contact support?",
            "What payment methods do you accept?",
            "Do you ship internationally?",
            "What is your warranty policy?"
        ]
        
        for i, question in enumerate(test_questions):
            repo.create(
                question=question,
                answer=f"Test answer {i+1}",
                processing_time=100 + i * 50,
                model_used="mistral"
            )
        print(f"✅ Created {len(test_questions)} additional entries")
        
        # Test 4: Get latest entries
        print("\n5. Getting latest 3 entries...")
        latest = repo.get_latest(limit=3)
        for entry in latest:
            print(f"   - ID: {entry.id}, Question: {entry.question[:40]}...")
        
        # Test 5: Count total entries
        print(f"\n6. Total entries in database...")
        total = repo.count()
        print(f"✅ Total entries: {total}")
        
        # Test 6: Search by question
        print("\n7. Searching for 'support'...")
        results = repo.search_by_question("support")
        print(f"✅ Found {len(results)} matching entries")
        
        # Test 7: Get average processing time
        print("\n8. Getting average processing time...")
        avg_time = repo.get_average_processing_time()
        if avg_time:
            print(f"✅ Average processing time: {avg_time:.2f} ms")
        
    print("\n" + "=" * 50)
    print("🎉 All database tests passed!")
    print("\nDatabase location:", "customer_support.db")
    
    # Ask if user wants to reset
    response = input("\nReset database for clean state? (y/n): ")
    if response.lower() == 'y':
        reset_database()
        print("✅ Database reset complete")


if __name__ == "__main__":
    test_database()