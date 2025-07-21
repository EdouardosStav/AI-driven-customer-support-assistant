"""
Test configuration and fixtures.
"""

import pytest
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.base import Base
from app.config import Settings
from app.main import app
from app.services.knowledge_base import KnowledgeBaseManager
from app.db.session import get_db


@pytest.fixture
def test_settings():
    """Test settings with temporary database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        test_db_path = tmp.name
    
    settings = Settings(
        database_url=f"sqlite:///{test_db_path}",
        knowledge_base_path=Path("./tests/fixtures/test_knowledge_base.md"),
        ollama_host="http://localhost:11434",
        log_level="DEBUG"
    )
    return settings


@pytest.fixture
def test_db_engine(test_settings):
    """Create test database engine."""
    engine = create_engine(
        test_settings.get_database_url(),
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db_session(test_db_engine):
    """Create test database session."""
    TestSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_knowledge_base():
    """Create test knowledge base file."""
    kb_content = """# Test Knowledge Base

Q: What is the refund policy?
A: Our refund policy allows customers to return products within 30 days of purchase with receipt.

Q: How can I contact support?
A: You can reach us at support@example.com or call 1-800-SUPPORT.

Q: What are your business hours?
A: We are open Monday through Friday, 9 AM to 5 PM EST.
"""
    
    # Create temporary knowledge base file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
        tmp.write(kb_content)
        kb_path = Path(tmp.name)
    
    yield kb_path
    
    # Cleanup
    kb_path.unlink(missing_ok=True)


@pytest.fixture
def knowledge_base_manager(test_knowledge_base):
    """Create knowledge base manager with test data."""
    manager = KnowledgeBaseManager(knowledge_base_path=test_knowledge_base)
    manager.load_knowledge_base()
    return manager


@pytest.fixture
def override_get_db(test_db_session):
    """Override the get_db dependency."""
    def _override_get_db():
        yield test_db_session
    return _override_get_db


@pytest.fixture
def test_client(override_get_db, knowledge_base_manager):
    """Create test client with overridden dependencies."""
    app.dependency_overrides[get_db] = override_get_db
    app.state.knowledge_base = knowledge_base_manager
    
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "answer": "This is a test response from the AI assistant.",
        "processing_time": 1000,
        "model_used": "mistral",
        "context_method": "keyword",
        "context_length": 500
    }