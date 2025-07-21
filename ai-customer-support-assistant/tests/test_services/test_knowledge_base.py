"""
Tests for knowledge base functionality.
"""

import pytest
from pathlib import Path

from app.services.knowledge_base import KnowledgeBaseManager, QAPair
from app.core.exceptions import KnowledgeBaseException


def test_qa_pair_creation():
    """Test QAPair creation and methods."""
    qa = QAPair("What is your name?", "My name is Assistant.", 0)
    
    assert qa.question == "What is your name?"
    assert qa.answer == "My name is Assistant."
    assert qa.index == 0
    
    qa_dict = qa.to_dict()
    assert qa_dict["question"] == "What is your name?"
    assert qa_dict["answer"] == "My name is Assistant."
    assert qa_dict["index"] == 0


def test_knowledge_base_loading(test_knowledge_base):
    """Test loading knowledge base from file."""
    manager = KnowledgeBaseManager(knowledge_base_path=test_knowledge_base)
    manager.load_knowledge_base()
    
    assert manager.is_loaded
    assert manager.qa_count == 3
    assert len(manager.qa_pairs) == 3


def test_knowledge_base_parsing(knowledge_base_manager):
    """Test knowledge base parsing functionality."""
    qa_pairs = knowledge_base_manager.get_all_qa_pairs()
    
    # Check first Q&A pair
    first_qa = qa_pairs[0]
    assert "refund policy" in first_qa["question"].lower()
    assert "30 days" in first_qa["answer"]


def test_knowledge_base_context_generation(knowledge_base_manager):
    """Test context generation for prompts."""
    context = knowledge_base_manager.get_context_for_prompt()
    
    assert "refund policy" in context.lower()
    assert "support@example.com" in context
    assert "Q:" in context
    assert "A:" in context


def test_knowledge_base_keyword_search(knowledge_base_manager):
    """Test keyword-based search functionality."""
    # Search for refund-related questions
    results = knowledge_base_manager.search_by_keywords("refund return", top_k=2)
    
    assert len(results) >= 1
    assert any("refund" in qa.question.lower() for qa in results)


def test_knowledge_base_relevant_context(knowledge_base_manager):
    """Test getting relevant context for queries."""
    # Test keyword method - should return relevant matches
    context = knowledge_base_manager.get_relevant_context(
        "I want to return my item", 
        method="keyword"
    )
    assert "refund" in context.lower()
    
    # Test all method - should return same or more content than keyword (when keyword finds matches)
    context_all = knowledge_base_manager.get_relevant_context(
        "test query", 
        method="all"
    )
    # For a test query with no matches, all method should return full context
    assert len(context_all) >= len(context)


def test_knowledge_base_file_not_found():
    """Test handling of missing knowledge base file."""
    manager = KnowledgeBaseManager(knowledge_base_path=Path("nonexistent.md"))
    
    with pytest.raises(KnowledgeBaseException):
        manager.load_knowledge_base()


def test_knowledge_base_empty_file():
    """Test handling of empty knowledge base file."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
        tmp.write("")
        empty_path = Path(tmp.name)
    
    try:
        manager = KnowledgeBaseManager(knowledge_base_path=empty_path)
        with pytest.raises(KnowledgeBaseException):
            manager.load_knowledge_base()
    finally:
        empty_path.unlink(missing_ok=True)


def test_knowledge_base_reload(knowledge_base_manager):
    """Test knowledge base reloading."""
    initial_count = knowledge_base_manager.qa_count
    
    # Reload should work without errors
    knowledge_base_manager.reload()
    
    assert knowledge_base_manager.qa_count == initial_count
    assert knowledge_base_manager.is_loaded