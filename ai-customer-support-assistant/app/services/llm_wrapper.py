"""
LLM Wrapper for Ollama/Mistral integration.

This module provides a clean interface to interact with the Mistral model
running on Ollama for generating customer support responses.
"""

import json
import time
from typing import Dict, List, Optional, Any

import httpx
from httpx import TimeoutException, HTTPStatusError

from app.config import settings
from app.core.exceptions import LLMException, OllamaConnectionException
from app.core.logging import get_logger
from app.services.knowledge_base import KnowledgeBaseManager
from app.utils.prompt_builder import PromptBuilder

logger = get_logger(__name__)


class OllamaClient:
    """
    Client for interacting with Ollama API.
    
    Handles HTTP communication with the Ollama service.
    """
    
    def __init__(self, base_url: str = None, timeout: int = None):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama API base URL (uses settings default if None)
            timeout: Request timeout in seconds (uses settings default if None)
        """
        self.base_url = base_url or settings.ollama_host
        self.timeout = timeout or settings.ollama_timeout
        self.model = settings.ollama_model
        
        # Create HTTP client with connection pooling
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
            headers={"Content-Type": "application/json"}
        )
        
        logger.info(f"Initialized Ollama client: {self.base_url}, model: {self.model}")
    
    def check_connection(self) -> bool:
        """
        Check if Ollama is accessible.
        
        Returns:
            True if Ollama is running and accessible
        """
        try:
            response = self.client.get("/")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection check failed: {e}")
            return False
    
    def check_model_available(self) -> bool:
        """
        Check if the specified model is available in Ollama.
        
        Returns:
            True if model is available
        """
        try:
            response = self.client.get("/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                # Handle model names with/without tags
                model_base = self.model.split(":")[0]
                return any(model_base in m for m in models)
            return False
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, retry_count: int = 2) -> str:
        """
        Generate text using Ollama with retry logic.
        
        Args:
            prompt: The prompt to send to the model
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate
            retry_count: Number of retries on timeout
            
        Returns:
            Generated text response
            
        Raises:
            OllamaConnectionException: If connection fails
            LLMException: If generation fails
        """
        last_exception = None
        
        for attempt in range(retry_count + 1):
            try:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                
                logger.debug(f"Sending request to Ollama: model={self.model}, prompt_length={len(prompt)}, attempt={attempt + 1}")
                
                response = self.client.post("/api/generate", json=payload)
                response.raise_for_status()
                
                data = response.json()
                generated_text = data.get("response", "")
                
                if not generated_text:
                    raise LLMException("Empty response from Ollama")
                
                logger.debug(f"Received response: length={len(generated_text)}")
                return generated_text.strip()
                
            except TimeoutException as e:
                last_exception = e
                if attempt < retry_count:
                    logger.warning(f"Request timeout (attempt {attempt + 1}/{retry_count + 1}), retrying...")
                    time.sleep(1)  # Brief pause before retry
                    continue
                raise OllamaConnectionException(
                    details={"error": "Request timeout after retries", "timeout": self.timeout, "attempts": retry_count + 1}
                )
            except HTTPStatusError as e:
                raise LLMException(
                    f"HTTP error from Ollama: {e.response.status_code}",
                    details={"status_code": e.response.status_code, "response": e.response.text}
                )
            except Exception as e:
                logger.exception("Unexpected error in Ollama generation")
                raise LLMException(f"Failed to generate response: {str(e)}")
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class CustomerSupportLLM:
    """
    High-level LLM wrapper for customer support responses.
    
    Integrates knowledge base context and prompt engineering.
    """
    
    def __init__(self, knowledge_base: Optional[KnowledgeBaseManager] = None):
        """
        Initialize the customer support LLM.
        
        Args:
            knowledge_base: Knowledge base manager instance
        """
        self.ollama_client = OllamaClient()
        self.knowledge_base = knowledge_base
        
        # Check Ollama connection on initialization
        if not self.ollama_client.check_connection():
            raise OllamaConnectionException(
                details={"message": "Please ensure Ollama is running"}
            )
        
        # Check model availability
        if not self.ollama_client.check_model_available():
            logger.warning(
                f"Model '{settings.ollama_model}' not found. "
                f"Run: ollama pull {settings.ollama_model}"
            )
    
    def build_prompt(self, question: str, context: str) -> str:
        """
        Build the prompt for the LLM with context and question.
        
        Args:
            question: User's question
            context: Relevant Q&A pairs from knowledge base
            
        Returns:
            Formatted prompt string
        """
        # Use the prompt builder for consistent formatting
        return PromptBuilder.build_customer_support_prompt(
            question=question,
            context=context,
            company_name="our company",
            include_examples=False
        )
    
    def answer_question(
        self,
        question: str,
        context_method: str = "keyword",
        temperature: float = 0.7,
        max_tokens: int = 300,
        max_context_pairs: int = 5  # Limit context size
    ) -> Dict[str, Any]:
        """
        Generate an answer to a customer question.
        
        Args:
            question: The customer's question
            context_method: Method for selecting context ("all", "keyword")
            temperature: LLM sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary with answer and metadata
        """
        start_time = time.time()
        
        try:
            # Get relevant context from knowledge base
            if self.knowledge_base and self.knowledge_base.is_loaded:
                if context_method == "all":
                    # Limit "all" context to prevent timeouts
                    context = self.knowledge_base.get_context_for_prompt(max_pairs=max_context_pairs)
                else:
                    context = self.knowledge_base.get_relevant_context(
                        question, 
                        method=context_method
                    )
                logger.info(f"Using {context_method} context selection, context length: {len(context)}")
            else:
                # Fallback if no knowledge base
                context = "No knowledge base loaded. Please provide general assistance."
                logger.warning("No knowledge base available")
            
            # Build prompt
            prompt = self.build_prompt(question, context)
            
            # Generate response
            answer = self.ollama_client.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)  # milliseconds
            
            return {
                "answer": answer,
                "processing_time": processing_time,
                "model_used": settings.ollama_model,
                "context_method": context_method,
                "context_length": len(context)
            }
            
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            raise
    
    def close(self):
        """Clean up resources."""
        self.ollama_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()