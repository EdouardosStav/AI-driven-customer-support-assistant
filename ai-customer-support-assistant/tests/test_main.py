"""
Tests for main application functionality.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_root_endpoint():
    """Test the root endpoint."""
    with TestClient(app) as client:
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"


def test_health_endpoint():
    """Test the health check endpoint."""
    with TestClient(app) as client:
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"


def test_request_id_middleware():
    """Test that request ID middleware adds headers."""
    with TestClient(app) as client:
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers


def test_cors_headers():
    """Test CORS headers are present."""
    with TestClient(app) as client:
        # Test with a GET request to see CORS headers
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        
        # Should have CORS headers in response
        assert response.status_code == 200
        # Check for access-control-allow-origin header (case insensitive)
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        assert "access-control-allow-origin" in headers_lower


def test_validation_error_handling():
    """Test validation error handling."""
    with TestClient(app) as client:
        # Send invalid JSON to trigger validation error
        response = client.post(
            "/api/v1/ask",
            json={"invalid_field": "value"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "details" in data
        assert "request_id" in data


def test_404_handling():
    """Test 404 error for non-existent endpoints."""
    with TestClient(app) as client:
        response = client.get("/nonexistent")
        
        assert response.status_code == 404


def test_openapi_schema():
    """Test that OpenAPI schema is accessible."""
    with TestClient(app) as client:
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


def test_docs_endpoint():
    """Test that API documentation is accessible."""
    with TestClient(app) as client:
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]