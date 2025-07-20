"""
Knowledge Base Manager for parsing and managing FAQ content.

This module handles loading, parsing, and providing access to the knowledge base
used by the LLM to answer customer queries.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.config import settings
from app.core.exceptions import KnowledgeBaseException
from app.core.logging import get_logger

logger = get_logger(__name__)


class QAPair:
    """Represents a single question-answer pair from the knowledge base."""
    
    def __init__(self, question: str, answer: str, index: int):
        self.question = question.strip()
        self.answer = answer.strip()
        self.index = index
        
    def __repr__(self) -> str:
        return f"QAPair(index={self.index}, question='{self.question[:50]}...')"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary representation."""
        return {
            "question": self.question,
            "answer": self.answer,
            "index": self.index
        }


class KnowledgeBaseManager:
    """
    Manages the knowledge base for the customer support assistant.
    
    This class handles:
    - Loading knowledge base from file
    - Parsing Q&A pairs
    - Providing formatted context for LLM prompts
    - (Future) Similarity search and context selection
    """
    
    def __init__(self, knowledge_base_path: Optional[Path] = None):
        """
        Initialize the Knowledge Base Manager.
        
        Args:
            knowledge_base_path: Path to knowledge base file (uses settings default if None)
        """
        self.knowledge_base_path = knowledge_base_path or settings.knowledge_base_path
        self.qa_pairs: List[QAPair] = []
        self._raw_content: str = ""
        
    def load_knowledge_base(self) -> None:
        """
        Load and parse the knowledge base from file.
        
        Raises:
            KnowledgeBaseException: If file cannot be loaded or parsed
        """
        try:
            logger.info(f"Loading knowledge base from: {self.knowledge_base_path}")
            
            if not self.knowledge_base_path.exists():
                raise KnowledgeBaseException(
                    f"Knowledge base file not found: {self.knowledge_base_path}"
                )
            
            # Read file content
            self._raw_content = self.knowledge_base_path.read_text(encoding='utf-8')
            
            # Parse Q&A pairs
            self.qa_pairs = self._parse_qa_pairs(self._raw_content)
            
            if not self.qa_pairs:
                raise KnowledgeBaseException(
                    "No Q&A pairs found in knowledge base"
                )
            
            logger.info(f"Successfully loaded {len(self.qa_pairs)} Q&A pairs")
            
        except Exception as e:
            if isinstance(e, KnowledgeBaseException):
                raise
            raise KnowledgeBaseException(
                f"Failed to load knowledge base: {str(e)}"
            )
    
    def _parse_qa_pairs(self, content: str) -> List[QAPair]:
        """
        Parse Q&A pairs from the knowledge base content.
        
        Args:
            content: Raw content from knowledge base file
            
        Returns:
            List of QAPair objects
        """
        qa_pairs = []
        
        # Remove any markdown headers or extra whitespace
        content = re.sub(r'^#.*$', '', content, flags=re.MULTILINE)
        
        # Split by "Q:" to find questions
        # Pattern matches Q: at the start of a line
        question_pattern = r'^Q:\s*(.+?)(?=^[QA]:|$)'
        answer_pattern = r'^A:\s*(.+?)(?=^[QA]:|$)'
        
        # Find all Q&A pairs using regex
        matches = re.findall(
            r'Q:\s*(.+?)\s*A:\s*(.+?)(?=\s*Q:|$)',
            content,
            re.DOTALL | re.MULTILINE
        )
        
        for index, (question, answer) in enumerate(matches):
            # Clean up the text
            question = self._clean_text(question)
            answer = self._clean_text(answer)
            
            if question and answer:
                qa_pairs.append(QAPair(question, answer, index))
                logger.debug(f"Parsed Q&A pair {index}: {question[:50]}...")
        
        return qa_pairs
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        # Remove any remaining markdown formatting
        text = re.sub(r'\*{1,2}([^\*]+)\*{1,2}', r'\1', text)  # Remove bold/italic
        text = re.sub(r'`([^`]+)`', r'\1', text)  # Remove inline code
        return text.strip()
    
    def get_all_qa_pairs(self) -> List[Dict[str, str]]:
        """
        Get all Q&A pairs as dictionaries.
        
        Returns:
            List of Q&A pair dictionaries
        """
        return [qa.to_dict() for qa in self.qa_pairs]
    
    def get_context_for_prompt(self, max_pairs: Optional[int] = None) -> str:
        """
        Get formatted context for LLM prompt.
        
        Args:
            max_pairs: Maximum number of Q&A pairs to include (None = all)
            
        Returns:
            Formatted string with Q&A pairs for prompt context
        """
        pairs_to_include = self.qa_pairs[:max_pairs] if max_pairs else self.qa_pairs
        
        context_parts = []
        for qa in pairs_to_include:
            context_parts.append(f"Q: {qa.question}")
            context_parts.append(f"A: {qa.answer}")
            context_parts.append("")  # Empty line between pairs
        
        return "\n".join(context_parts).strip()
    
    def search_by_keywords(self, query: str, top_k: int = 5) -> List[QAPair]:
        """
        Simple keyword-based search for relevant Q&A pairs.
        
        Args:
            query: User query to match against
            top_k: Number of top results to return
            
        Returns:
            List of most relevant QAPair objects
        """
        query_words = set(query.lower().split())
        
        # Score each Q&A pair based on keyword matches
        scored_pairs = []
        for qa in self.qa_pairs:
            question_words = set(qa.question.lower().split())
            answer_words = set(qa.answer.lower().split())
            
            # Count matching words (question matches weighted higher)
            question_matches = len(query_words & question_words)
            answer_matches = len(query_words & answer_words)
            score = (question_matches * 2) + answer_matches
            
            if score > 0:
                scored_pairs.append((score, qa))
        
        # Sort by score and return top k
        scored_pairs.sort(key=lambda x: x[0], reverse=True)
        return [qa for _, qa in scored_pairs[:top_k]]
    
    def get_relevant_context(self, query: str, method: str = "all") -> str:
        """
        Get relevant context for a user query.
        
        Args:
            query: User query
            method: Context selection method ("all", "keyword", "similarity")
            
        Returns:
            Formatted context string
        """
        if method == "all":
            return self.get_context_for_prompt()
        elif method == "keyword":
            relevant_pairs = self.search_by_keywords(query)
            if not relevant_pairs:
                # Fall back to all context if no matches
                logger.warning(f"No keyword matches for query: {query}")
                return self.get_context_for_prompt()
            
            context_parts = []
            for qa in relevant_pairs:
                context_parts.append(f"Q: {qa.question}")
                context_parts.append(f"A: {qa.answer}")
                context_parts.append("")
            
            return "\n".join(context_parts).strip()
        elif method == "similarity":
            # Placeholder for future similarity search
            raise NotImplementedError("Similarity search not yet implemented")
        else:
            raise ValueError(f"Unknown context selection method: {method}")
    
    def reload(self) -> None:
        """Reload the knowledge base from file."""
        logger.info("Reloading knowledge base...")
        self.qa_pairs.clear()
        self.load_knowledge_base()
    
    @property
    def is_loaded(self) -> bool:
        """Check if knowledge base is loaded."""
        return len(self.qa_pairs) > 0
    
    @property
    def qa_count(self) -> int:
        """Get the number of Q&A pairs loaded."""
        return len(self.qa_pairs)