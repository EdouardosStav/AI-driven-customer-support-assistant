"""
Main FastAPI application entry point.

This module initializes the FastAPI application with all routes,
middleware, and exception handlers.
"""

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__, settings
from app.api.routes import ask, history
from app.core.exceptions import AppException
from app.core.logging import get_logger, setup_logging
from app.db.init_db import init_db
from app.services.knowledge_base import KnowledgeBaseManager

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting AI Customer Support Assistant...")
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Load knowledge base
    logger.info(f"Loading knowledge base from {settings.knowledge_base_path}...")
    try:
        kb_manager = KnowledgeBaseManager()
        kb_manager.load_knowledge_base()
        # Store in app state for access in routes
        app.state.knowledge_base = kb_manager
        logger.info(f"Loaded {len(kb_manager.qa_pairs)} Q&A pairs from knowledge base")
    except Exception as e:
        logger.error(f"Failed to load knowledge base: {e}")
        # Continue startup even if knowledge base fails to load
        app.state.knowledge_base = None
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Customer Support Assistant...")
    # Add any cleanup code here
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="AI-driven customer support assistant using Mistral LLM via Ollama",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware (configure as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request for tracing."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add request ID to logger
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={"request_id": request_id}
    )
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.info(
        f"Request completed: {request.method} {request.url.path} - {response.status_code}",
        extra={
            "request_id": request_id,
            "process_time": process_time,
            "status_code": response.status_code
        }
    )
    
    return response


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application-specific exceptions."""
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "details": exc.details
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"request_id": getattr(request.state, "request_id", None)}
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation failed",
            "details": exc.errors(),
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception(
        f"Unexpected error: {str(exc)}",
        extra={"request_id": getattr(request.state, "request_id", None)}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None)
        }
    )


# Include routers
app.include_router(
    ask.router,
    prefix=f"{settings.api_prefix}",
    tags=["Questions"]
)

app.include_router(
    history.router,
    prefix=f"{settings.api_prefix}",
    tags=["History"]
)


# Root endpoint
@app.get("/", tags=["Health"])
async def root() -> Dict[str, Any]:
    """Root endpoint providing API information."""
    return {
        "name": settings.app_name,
        "version": __version__,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )