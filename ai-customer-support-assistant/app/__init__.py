"""
AI Customer Support Assistant - Backend Service

A FastAPI-based backend service that uses Mistral LLM via Ollama
to answer customer queries based on a local knowledge base.
"""

__version__ = "0.1.0"
__author__ = "Edouardos Stavrakis"
__email__ = "edouardos.stavrakis@gmail.com"

# Import key components for easier access
from app.config import settings

__all__ = ["settings", "__version__"]