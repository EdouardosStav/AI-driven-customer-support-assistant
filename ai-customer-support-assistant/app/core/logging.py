"""
Logging configuration for the application.

Sets up structured logging with both console and file outputs.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict

try:
    from pythonjsonlogger import jsonlogger
    JSON_LOGGING_AVAILABLE = True
except ImportError:
    JSON_LOGGING_AVAILABLE = False
    import json

from app.config import settings


if JSON_LOGGING_AVAILABLE:
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        """Custom JSON formatter with additional fields."""
        
        def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
            """Add custom fields to log records."""
            super().add_fields(log_record, record, message_dict)
            log_record['app_name'] = settings.app_name
            log_record['app_version'] = settings.app_version
            if hasattr(record, 'request_id'):
                log_record['request_id'] = record.request_id
else:
    # Fallback formatter if pythonjsonlogger is not available
    class CustomJsonFormatter(logging.Formatter):
        """Fallback JSON formatter."""
        
        def format(self, record: logging.LogRecord) -> str:
            log_obj = {
                'timestamp': self.formatTime(record),
                'level': record.levelname,
                'name': record.name,
                'message': record.getMessage(),
                'app_name': settings.app_name,
                'app_version': settings.app_version
            }
            if hasattr(record, 'request_id'):
                log_obj['request_id'] = record.request_id
            return json.dumps(log_obj)


def setup_logging() -> None:
    """
    Configure logging for the application.
    
    Sets up both console and file logging with appropriate formatters.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_file_path).parent
    log_dir.mkdir(exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler with standard formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with JSON formatting and rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=settings.log_file_path,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding='utf-8'
    )
    if JSON_LOGGING_AVAILABLE:
        json_formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            timestamp=True
        )
    else:
        json_formatter = CustomJsonFormatter()
    file_handler.setFormatter(json_formatter)
    root_logger.addHandler(file_handler)
    
    # Set specific log levels for third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.database_echo else logging.WARNING
    )
    
    # Log startup message
    root_logger.info(
        "Logging initialized",
        extra={
            "log_level": settings.log_level,
            "log_file": str(settings.log_file_path)
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)