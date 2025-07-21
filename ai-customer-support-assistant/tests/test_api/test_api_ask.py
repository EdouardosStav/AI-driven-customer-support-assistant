"""
Tests for the /ask API endpoint.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.llm_wrapper import CustomerSupportLLM


class TestAskEndpoint:
    """Test cases for the /ask endpoint."""
    
    def test_ask_endpoint_success(self, test_client, mock_llm_response):
        """Test successful question processing."""
        
        # Mock the LLM to avoid needing Ollama running
        with patch.object(CustomerSupportLLM, 'answer_question', return_value=mock_llm_response), \
             patch.object(CustomerSupportLLM, 'close'):
            
            response = test_client.post(
                "/api/v1/ask",
                json={"question": "What is your refund policy?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "answer" in data
            assert "question_id" in data
            assert "timestamp" in data
            assert "processing_time" in data
            assert data["answer"] == mock_llm_response["answer"]
    
    def test_ask_endpoint_with_context_method(self, test_client, mock_llm_response):
        """Test ask endpoint with specific context method."""
        
        with patch.object(CustomerSupportLLM, 'answer_question', return_value=mock_llm_response), \
             patch.object(CustomerSupportLLM, 'close'):
            
            response = test_client.post(
                "/api/v1/ask",
                json={
                    "question": "How can I contact support?",
                    "context_method": "all"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
    
    def test_ask_endpoint_validation_errors(self, test_client):
        """Test validation errors for invalid requests."""
        
        # Empty question
        response = test_client.post(
            "/api/v1/ask",
            json={"question": ""}
        )
        assert response.status_code == 422
        
        # Question too long
        response = test_client.post(
            "/api/v1/ask",
            json={"question": "x" * 501}
        )
        assert response.status_code == 422
        
        # Invalid context method
        response = test_client.post(
            "/api/v1/ask",
            json={
                "question": "Valid question?",
                "context_method": "invalid"
            }
        )
        assert response.status_code == 422
    
    def test_ask_endpoint_missing_question(self, test_client):
        """Test request without question field."""
        
        response = test_client.post(
            "/api/v1/ask",
            json={}
        )
        
        assert response.status_code == 422
        error_data = response.json()
        # The error response structure has 'details' field, not 'detail'
        assert "details" in error_data or "detail" in error_data
    
    def test_ask_endpoint_only_punctuation(self, test_client):
        """Test question with only punctuation."""
        
        response = test_client.post(
            "/api/v1/ask",
            json={"question": "???!!!"}
        )
        
        assert response.status_code == 422
    
    def test_ask_endpoint_llm_error(self, test_client):
        """Test handling of LLM errors."""
        
        with patch.object(CustomerSupportLLM, '__init__', side_effect=Exception("LLM Error")):
            
            response = test_client.post(
                "/api/v1/ask",
                json={"question": "What is your refund policy?"}
            )
            
            assert response.status_code == 500
    
    def test_ask_endpoint_no_knowledge_base(self, test_client):
        """Test behavior when knowledge base is not loaded."""
        
        # Temporarily remove knowledge base
        original_kb = test_client.app.state.knowledge_base
        test_client.app.state.knowledge_base = None
        
        try:
            response = test_client.post(
                "/api/v1/ask",
                json={"question": "What is your refund policy?"}
            )
            
            # The HTTPException gets caught by general exception handler, returning 500
            assert response.status_code == 500
            error_data = response.json()
            # Check for either 'error' or 'detail' field (different exception handlers use different formats)
            assert "error" in error_data or "detail" in error_data
        
        finally:
            # Restore knowledge base
            test_client.app.state.knowledge_base = original_kb
    
    def test_ask_endpoint_database_error_still_returns_answer(self, test_client, mock_llm_response):
        """Test that answer is still returned even if database storage fails."""
        
        with patch.object(CustomerSupportLLM, 'answer_question', return_value=mock_llm_response), \
             patch.object(CustomerSupportLLM, 'close'), \
             patch('app.api.routes.ask.QueryRepository.create', side_effect=Exception("DB Error")):
            
            response = test_client.post(
                "/api/v1/ask",
                json={"question": "What is your refund policy?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["answer"] == mock_llm_response["answer"]
            assert data["question_id"] == 0  # Indicates DB storage failed
    
    def test_ask_endpoint_whitespace_handling(self, test_client, mock_llm_response):
        """Test handling of questions with extra whitespace."""
        
        with patch.object(CustomerSupportLLM, 'answer_question', return_value=mock_llm_response), \
             patch.object(CustomerSupportLLM, 'close'):
            
            response = test_client.post(
                "/api/v1/ask",
                json={"question": "  What is your refund policy?  "}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data