"""
Tests for LLM wrapper functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
import httpx

from app.services.llm_wrapper import OllamaClient, CustomerSupportLLM
from app.core.exceptions import LLMException, OllamaConnectionException


class TestOllamaClient:
    """Test cases for OllamaClient."""
    
    def test_ollama_client_initialization(self):
        """Test OllamaClient initialization."""
        client = OllamaClient(
            base_url="http://localhost:11434",
            timeout=30
        )
        
        assert client.base_url == "http://localhost:11434"
        assert client.timeout == 30
        assert client.model == "mistral"  # from settings
        
        client.close()
    
    @patch('httpx.Client.get')
    def test_check_connection_success(self, mock_get):
        """Test successful connection check."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        result = client.check_connection()
        
        assert result is True
        client.close()
    
    @patch('httpx.Client.get')
    def test_check_connection_failure(self, mock_get):
        """Test failed connection check."""
        mock_get.side_effect = Exception("Connection failed")
        
        client = OllamaClient()
        result = client.check_connection()
        
        assert result is False
        client.close()
    
    @patch('httpx.Client.get')
    def test_check_model_available_success(self, mock_get):
        """Test successful model availability check."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "mistral:latest"},
                {"name": "llama2:7b"}
            ]
        }
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        result = client.check_model_available()
        
        assert result is True
        client.close()
    
    @patch('httpx.Client.get')
    def test_check_model_available_not_found(self, mock_get):
        """Test model not available."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2:7b"}
            ]
        }
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        result = client.check_model_available()
        
        assert result is False
        client.close()
    
    @patch('httpx.Client.post')
    def test_generate_success(self, mock_post):
        """Test successful text generation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "This is a test response from Mistral."
        }
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        result = client.generate("Test prompt")
        
        assert result == "This is a test response from Mistral."
        client.close()
    
    @patch('httpx.Client.post')
    def test_generate_timeout_with_retry(self, mock_post):
        """Test generation with timeout and retry."""
        # First call times out, second succeeds
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Success after retry"}
        
        mock_post.side_effect = [
            httpx.TimeoutException("Timeout"),
            mock_response
        ]
        
        client = OllamaClient()
        result = client.generate("Test prompt", retry_count=1)
        
        assert result == "Success after retry"
        assert mock_post.call_count == 2
        client.close()
    
    @patch('httpx.Client.post')
    def test_generate_timeout_exhausted_retries(self, mock_post):
        """Test generation with timeout after all retries exhausted."""
        mock_post.side_effect = httpx.TimeoutException("Timeout")
        
        client = OllamaClient()
        
        with pytest.raises(OllamaConnectionException):
            client.generate("Test prompt", retry_count=1)
        
        assert mock_post.call_count == 2  # Initial + 1 retry
        client.close()
    
    @patch('httpx.Client.post')
    def test_generate_http_error(self, mock_post):
        """Test generation with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_post.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        )
        
        client = OllamaClient()
        
        with pytest.raises(LLMException):
            client.generate("Test prompt")
        
        client.close()
    
    @patch('httpx.Client.post')
    def test_generate_empty_response(self, mock_post):
        """Test generation with empty response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": ""}
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        
        with pytest.raises(LLMException):
            client.generate("Test prompt")
        
        client.close()


class TestCustomerSupportLLM:
    """Test cases for CustomerSupportLLM."""
    
    @patch.object(OllamaClient, 'check_connection', return_value=True)
    @patch.object(OllamaClient, 'check_model_available', return_value=True)
    def test_customer_support_llm_initialization(self, mock_check_model, mock_check_connection, knowledge_base_manager):
        """Test CustomerSupportLLM initialization."""
        llm = CustomerSupportLLM(knowledge_base=knowledge_base_manager)
        
        assert llm.knowledge_base == knowledge_base_manager
        mock_check_connection.assert_called_once()
        mock_check_model.assert_called_once()
        
        llm.close()
    
    @patch.object(OllamaClient, 'check_connection', return_value=False)
    def test_customer_support_llm_connection_error(self, mock_check_connection):
        """Test initialization with connection error."""
        with pytest.raises(OllamaConnectionException):
            CustomerSupportLLM()
    
    def test_build_prompt(self, knowledge_base_manager):
        """Test prompt building functionality."""
        with patch.object(OllamaClient, 'check_connection', return_value=True), \
             patch.object(OllamaClient, 'check_model_available', return_value=True):
            
            llm = CustomerSupportLLM(knowledge_base=knowledge_base_manager)
            
            prompt = llm.build_prompt(
                question="What is your refund policy?",
                context="Q: Refund policy?\nA: 30 days return policy."
            )
            
            assert "What is your refund policy?" in prompt
            assert "30 days return policy" in prompt
            assert "customer support assistant" in prompt.lower()
            
            llm.close()
    
    @patch.object(OllamaClient, 'check_connection', return_value=True)
    @patch.object(OllamaClient, 'check_model_available', return_value=True)
    @patch.object(OllamaClient, 'generate')
    def test_answer_question_with_knowledge_base(self, mock_generate, mock_check_model, mock_check_connection, knowledge_base_manager):
        """Test answering question with knowledge base."""
        mock_generate.return_value = "Our refund policy allows returns within 30 days."
        
        llm = CustomerSupportLLM(knowledge_base=knowledge_base_manager)
        
        result = llm.answer_question(
            question="What is your refund policy?",
            context_method="keyword",
            temperature=0.3,
            max_tokens=300
        )
        
        assert "answer" in result
        assert "processing_time" in result
        assert "model_used" in result
        assert "context_method" in result
        assert "context_length" in result
        
        assert result["answer"] == "Our refund policy allows returns within 30 days."
        assert result["context_method"] == "keyword"
        
        llm.close()
    
    @patch.object(OllamaClient, 'check_connection', return_value=True)
    @patch.object(OllamaClient, 'check_model_available', return_value=True)
    @patch.object(OllamaClient, 'generate')
    def test_answer_question_without_knowledge_base(self, mock_generate, mock_check_model, mock_check_connection):
        """Test answering question without knowledge base."""
        mock_generate.return_value = "I don't have access to the knowledge base."
        
        llm = CustomerSupportLLM(knowledge_base=None)
        
        result = llm.answer_question(
            question="What is your refund policy?",
            context_method="all"
        )
        
        assert "answer" in result
        assert result["answer"] == "I don't have access to the knowledge base."
        
        llm.close()
    
    @patch.object(OllamaClient, 'check_connection', return_value=True)
    @patch.object(OllamaClient, 'check_model_available', return_value=True)
    @patch.object(OllamaClient, 'generate')
    def test_answer_question_all_context_method(self, mock_generate, mock_check_model, mock_check_connection, knowledge_base_manager):
        """Test answering question with 'all' context method."""
        mock_generate.return_value = "Here's comprehensive information about our policies."
        
        llm = CustomerSupportLLM(knowledge_base=knowledge_base_manager)
        
        result = llm.answer_question(
            question="Tell me about your policies",
            context_method="all"
        )
        
        assert result["context_method"] == "all"
        # Should limit context size for 'all' method
        mock_generate.assert_called_once()
        
        llm.close()
    
    @patch.object(OllamaClient, 'check_connection', return_value=True)
    @patch.object(OllamaClient, 'check_model_available', return_value=True)
    @patch.object(OllamaClient, 'generate', side_effect=Exception("Generation failed"))
    def test_answer_question_llm_error(self, mock_generate, mock_check_model, mock_check_connection, knowledge_base_manager):
        """Test handling of LLM generation errors."""
        llm = CustomerSupportLLM(knowledge_base=knowledge_base_manager)
        
        with pytest.raises(Exception):
            llm.answer_question("What is your refund policy?")
        
        llm.close()
    
    @patch.object(OllamaClient, 'check_connection', return_value=True)
    @patch.object(OllamaClient, 'check_model_available', return_value=True)
    def test_context_manager(self, mock_check_model, mock_check_connection, knowledge_base_manager):
        """Test using CustomerSupportLLM as context manager."""
        with CustomerSupportLLM(knowledge_base=knowledge_base_manager) as llm:
            assert llm.knowledge_base == knowledge_base_manager