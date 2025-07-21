"""
Tests for the /history API endpoint.
"""

import pytest
from unittest.mock import patch

from app.db.repositories.query_repository import QueryRepository


class TestHistoryEndpoint:
    """Test cases for the /history endpoint."""
    
    def test_history_endpoint_default(self, test_client):
        """Test history endpoint with default parameters."""
        
        response = test_client.get("/api/v1/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "entries" in data
        assert "count" in data
        assert "total" in data
        assert isinstance(data["entries"], list)
        assert data["count"] == len(data["entries"])
    
    def test_history_endpoint_with_limit(self, test_client):
        """Test history endpoint with custom limit."""
        
        response = test_client.get("/api/v1/history?n=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["entries"]) <= 5
        assert data["count"] <= 5
    
    def test_history_endpoint_with_data(self, test_client, test_db_session):
        """Test history endpoint with actual data in database."""
        
        # Add some test data
        repo = QueryRepository(test_db_session)
        for i in range(3):
            repo.create(
                question=f"Test question {i}?",
                answer=f"Test answer {i}.",
                processing_time=1000 + (i * 100),
                model_used="mistral"
            )
        
        response = test_client.get("/api/v1/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["entries"]) == 3
        assert data["count"] == 3
        assert data["total"] == 3
        
        # Check structure of first entry
        entry = data["entries"][0]
        assert "id" in entry
        assert "question" in entry
        assert "answer" in entry
        assert "timestamp" in entry
        assert "processing_time" in entry
        
        # Should be in reverse chronological order (newest first)
        assert "Test question 2" in entry["question"]
    
    def test_history_endpoint_search(self, test_client, test_db_session):
        """Test history endpoint with search functionality."""
        
        # Add test data with different questions
        repo = QueryRepository(test_db_session)
        repo.create(question="What is the refund policy?", answer="30 days return")
        repo.create(question="How to contact support?", answer="Email us")
        repo.create(question="What are shipping costs?", answer="Free shipping")
        
        # Search for refund-related questions
        response = test_client.get("/api/v1/history?search=refund")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] >= 1
        assert any("refund" in entry["question"].lower() for entry in data["entries"])
    
    def test_history_endpoint_validation_errors(self, test_client):
        """Test validation errors for invalid parameters."""
        
        # Negative limit
        response = test_client.get("/api/v1/history?n=-1")
        assert response.status_code == 422
        
        # Limit too high
        response = test_client.get("/api/v1/history?n=101")
        assert response.status_code == 422
        
        # Search term too short
        response = test_client.get("/api/v1/history?search=a")
        assert response.status_code == 422
        
        # Search term too long
        response = test_client.get("/api/v1/history?search=" + "x" * 101)
        assert response.status_code == 422
    
    def test_history_endpoint_empty_database(self, test_client):
        """Test history endpoint with empty database."""
        
        response = test_client.get("/api/v1/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["entries"] == []
        assert data["count"] == 0
        assert data["total"] == 0
    
    def test_history_endpoint_large_limit(self, test_client, test_db_session):
        """Test history endpoint with limit larger than available data."""
        
        # Add only 2 entries
        repo = QueryRepository(test_db_session)
        repo.create(question="Question 1?", answer="Answer 1")
        repo.create(question="Question 2?", answer="Answer 2")
        
        # Request 10 entries
        response = test_client.get("/api/v1/history?n=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["entries"]) == 2
        assert data["count"] == 2
        assert data["total"] == 2
    
    def test_history_endpoint_search_no_results(self, test_client, test_db_session):
        """Test search with no matching results."""
        
        # Add test data
        repo = QueryRepository(test_db_session)
        repo.create(question="What is the refund policy?", answer="30 days")
        
        # Search for non-existent term
        response = test_client.get("/api/v1/history?search=nonexistent")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["entries"] == []
        assert data["count"] == 0
    
    def test_history_endpoint_database_error(self, test_client):
        """Test handling of database errors."""
        
        with patch('app.api.routes.history.QueryRepository.get_latest', side_effect=Exception("DB Error")):
            
            response = test_client.get("/api/v1/history")
            
            assert response.status_code == 500
            error_data = response.json()
            assert "Failed to retrieve history" in error_data["detail"]
    
    def test_history_entry_timestamp_format(self, test_client, test_db_session):
        """Test that timestamps are properly formatted in ISO format."""
        
        # Add test entry
        repo = QueryRepository(test_db_session)
        repo.create(question="Test question?", answer="Test answer")
        
        response = test_client.get("/api/v1/history")
        
        assert response.status_code == 200
        data = response.json()
        
        entry = data["entries"][0]
        timestamp = entry["timestamp"]
        
        # Should end with 'Z' and be a valid ISO format
        assert timestamp.endswith("Z")
        assert "T" in timestamp
        assert len(timestamp) > 19  # Basic length check for ISO format