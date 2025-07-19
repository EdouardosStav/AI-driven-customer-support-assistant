"""
Configuration management for the AI Customer Support Assistant.

This module handles all configuration settings using Pydantic Settings
for type safety and environment variable support.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

try:
    # Pydantic v2
    from pydantic_settings import BaseSettings, SettingsConfigDict
    PYDANTIC_V2 = True
except ImportError:
    # Pydantic v1
    from pydantic import BaseSettings
    PYDANTIC_V2 = False


if PYDANTIC_V2:
    class Settings(BaseSettings):
        """Application settings with environment variable support."""
        
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
        )
        
        # Application Settings
        app_name: str = "AI Customer Support Assistant"
        app_version: str = "0.1.0"
        debug: bool = False
        log_level: str = "INFO"
        
        # API Configuration
        api_host: str = "0.0.0.0"
        api_port: int = 8000
        api_prefix: str = "/api/v1"
        
        # Database Configuration
        database_url: str = "sqlite:///./customer_support.db"
        database_echo: bool = False
        
        # Ollama Configuration
        ollama_host: str = "http://localhost:11434"
        ollama_model: str = "mistral"
        ollama_timeout: int = 30
        
        # Knowledge Base
        knowledge_base_path: Path = Path("./data/knowledge_base.md")
        
        # Security
        secret_key: str = "your-secret-key-here"
        
        # Logging
        log_file_path: Path = Path("./logs/app.log")
        log_max_bytes: int = 10485760  # 10MB
        log_backup_count: int = 5
        
        # Optional: ML Features
        enable_similarity_search: bool = False
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
else:
    class Settings(BaseSettings):
        """Application settings with environment variable support."""
        
        # Application Settings
        app_name: str = "AI Customer Support Assistant"
        app_version: str = "0.1.0"
        debug: bool = False
        log_level: str = "INFO"
        
        # API Configuration
        api_host: str = "0.0.0.0"
        api_port: int = 8000
        api_prefix: str = "/api/v1"
        
        # Database Configuration
        database_url: str = "sqlite:///./customer_support.db"
        database_echo: bool = False
        
        # Ollama Configuration
        ollama_host: str = "http://localhost:11434"
        ollama_model: str = "mistral"
        ollama_timeout: int = 30
        
        # Knowledge Base
        knowledge_base_path: Path = Path("./data/knowledge_base.md")
        
        # Security
        secret_key: str = "your-secret-key-here"
        
        # Logging
        log_file_path: Path = Path("./logs/app.log")
        log_max_bytes: int = 10485760  # 10MB
        log_backup_count: int = 5
        
        # Optional: ML Features
        enable_similarity_search: bool = False
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
        
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False
            extra = "ignore"


# Common methods for both versions
Settings.ollama_api_generate = property(lambda self: f"{self.ollama_host}/api/generate")
Settings.ollama_api_chat = property(lambda self: f"{self.ollama_host}/api/chat")

def _get_database_url(self) -> str:
    """Get the database URL with absolute SQLite path if needed."""
    if self.database_url.startswith("sqlite:///"):
        relative_path = self.database_url.replace("sqlite:///", "")
        absolute_path = Path(relative_path).resolve()
        return f"sqlite:///{absolute_path.as_posix()}"
    return self.database_url


Settings.get_database_url = _get_database_url


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Application settings
    """
    return Settings()


# Create a global settings instance
settings = get_settings()