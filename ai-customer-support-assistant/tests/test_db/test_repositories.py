"""
Tests for database repositories.
"""

import pytest
from datetime import datetime, timedelta

from app.db.repositories.query_repository import QueryRepository
from app.models.query_log import QueryLog


def test_query_repository_create(test_db_session):
    """Test creating a new query log entry."""
    repo = QueryRepository(test_db_session)
    
    query_log = repo.create(
        question="What is your refund policy?",
        answer="Our refund policy allows returns within 30 days.",
        processing_time=1500,
        model_used="mistral",
        context_used="keyword search, 3 entries"
    )
    
    assert query_log.id is not None
    assert query_log.question == "What is your refund policy?"
    assert query_log.answer == "Our refund policy allows returns within 30 days."
    assert query_log.processing_time == 1500
    assert query_log.model_used == "mistral"
    assert query_log.question_length == len("What is your refund policy?")
    assert query_log.answer_length == len("Our refund policy allows returns within 30 days.")


def test_query_repository_get_by_id(test_db_session):
    """Test retrieving query log by ID."""
    repo = QueryRepository(test_db_session)
    
    # Create entry
    created = repo.create(
        question="Test question",
        answer="Test answer"
    )
    
    # Retrieve by ID
    retrieved = repo.get_by_id(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.question == "Test question"
    assert retrieved.answer == "Test answer"


def test_query_repository_get_latest(test_db_session):
    """Test retrieving latest query logs."""
    repo = QueryRepository(test_db_session)
    
    # Create multiple entries
    for i in range(5):
        repo.create(
            question=f"Question {i}",
            answer=f"Answer {i}"
        )
    
    # Get latest 3
    latest = repo.get_latest(limit=3)
    
    assert len(latest) == 3
    # Should be in reverse chronological order
    assert "Question 4" in latest[0].question
    assert "Question 3" in latest[1].question
    assert "Question 2" in latest[2].question


def test_query_repository_get_all_with_pagination(test_db_session):
    """Test retrieving all query logs with pagination."""
    repo = QueryRepository(test_db_session)
    
    # Create entries
    for i in range(10):
        repo.create(
            question=f"Question {i}",
            answer=f"Answer {i}"
        )
    
    # Get first page
    first_page = repo.get_all(skip=0, limit=5)
    assert len(first_page) == 5
    
    # Get second page
    second_page = repo.get_all(skip=5, limit=5)
    assert len(second_page) == 5
    
    # Ensure different entries
    first_ids = {entry.id for entry in first_page}
    second_ids = {entry.id for entry in second_page}
    assert first_ids.isdisjoint(second_ids)


def test_query_repository_count(test_db_session):
    """Test counting total query logs."""
    repo = QueryRepository(test_db_session)
    
    # Initially empty
    assert repo.count() == 0
    
    # Add entries
    for i in range(3):
        repo.create(
            question=f"Question {i}",
            answer=f"Answer {i}"
        )
    
    assert repo.count() == 3


def test_query_repository_search_by_question(test_db_session):
    """Test searching query logs by question content."""
    repo = QueryRepository(test_db_session)
    
    # Create entries with different questions
    repo.create(question="What is the refund policy?", answer="30 days")
    repo.create(question="How to contact support?", answer="Email us")
    repo.create(question="What are shipping costs?", answer="Free shipping")
    
    # Search for refund-related questions
    results = repo.search_by_question("refund")
    
    assert len(results) == 1
    assert "refund" in results[0].question.lower()


def test_query_repository_get_by_date_range(test_db_session):
    """Test retrieving query logs by date range."""
    repo = QueryRepository(test_db_session)
    
    # Create an entry
    entry = repo.create(
        question="Test question",
        answer="Test answer"
    )
    
    # Define date range around the entry
    start_date = entry.timestamp - timedelta(hours=1)
    end_date = entry.timestamp + timedelta(hours=1)
    
    results = repo.get_by_date_range(start_date, end_date)
    
    assert len(results) == 1
    assert results[0].id == entry.id


def test_query_repository_get_average_processing_time(test_db_session):
    """Test calculating average processing time."""
    repo = QueryRepository(test_db_session)
    
    # Initially no entries with processing time
    assert repo.get_average_processing_time() is None
    
    # Add entries with processing times
    repo.create(question="Q1", answer="A1", processing_time=1000)
    repo.create(question="Q2", answer="A2", processing_time=2000)
    repo.create(question="Q3", answer="A3", processing_time=3000)
    
    avg_time = repo.get_average_processing_time()
    assert avg_time == 2000.0


def test_query_repository_create_minimal(test_db_session):
    """Test creating query log with minimal required fields."""
    repo = QueryRepository(test_db_session)
    
    query_log = repo.create(
        question="Simple question?",
        answer="Simple answer."
    )
    
    assert query_log.id is not None
    assert query_log.processing_time is None
    assert query_log.model_used == "mistral"  # default
    assert query_log.context_used is None
    assert isinstance(query_log.timestamp, datetime)