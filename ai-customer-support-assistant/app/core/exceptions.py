"""
Custom exceptions for the application.

Defines application-specific exceptions for better error handling.
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception for all application exceptions."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class LLMException(AppException):
    """Exception raised when LLM operations fail."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"LLM Error: {message}",
            status_code=503,
            details=details
        )


class KnowledgeBaseException(AppException):
    """Exception raised when knowledge base operations fail."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Knowledge Base Error: {message}",
            status_code=500,
            details=details
        )


class DatabaseException(AppException):
    """Exception raised when database operations fail."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Database Error: {message}",
            status_code=500,
            details=details
        )


class ValidationException(AppException):
    """Exception raised when validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Validation Error: {message}",
            status_code=400,
            details=details
        )


class OllamaConnectionException(LLMException):
    """Exception raised when Ollama connection fails."""
    
    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message="Failed to connect to Ollama. Please ensure Ollama is running.",
            details=details
        )