"""
Prompt builder utilities for LLM interactions.

This module provides various prompt templates and builders
for different types of customer support scenarios.
"""

from typing import List, Dict, Optional


class PromptBuilder:
    """Builder for creating structured prompts for the LLM."""
    
    @staticmethod
    def build_customer_support_prompt(
        question: str,
        context: str,
        company_name: str = "our company",
        include_examples: bool = False
    ) -> str:
        """
        Build a customer support prompt with context.
        
        Args:
            question: User's question
            context: Relevant Q&A pairs from knowledge base
            company_name: Company name for personalization
            include_examples: Whether to include example interactions
            
        Returns:
            Formatted prompt string
        """
        base_prompt = f"""You are a helpful customer support assistant for {company_name}. Use the following knowledge base to answer the customer's question accurately and concisely.

Knowledge Base:
{context}

Instructions:
1. Answer based ONLY on the information provided in the knowledge base above
2. If the exact answer isn't in the knowledge base, provide the most relevant information available
3. Be concise and direct in your response
4. Maintain a professional and friendly tone
5. If you cannot find relevant information, politely say so and suggest contacting support directly
6. Do not make up information that isn't in the knowledge base"""

        if include_examples:
            base_prompt += """

Example interactions:
Q: Do you offer student discounts?
A: I don't see information about student discounts in our knowledge base. For questions about special discounts, please contact our support team at support@example.com for the most accurate information.

Q: What's your return policy?
A: According to our policy, customers can return products within 30 days of purchase. The item must be in its original condition with all packaging intact. Once we receive the returned item, we will process your refund within 5-7 business days."""

        base_prompt += f"""

Customer Question: {question}

Answer:"""
        
        return base_prompt
    
    @staticmethod
    def build_fallback_prompt(question: str) -> str:
        """
        Build a fallback prompt when no knowledge base is available.
        
        Args:
            question: User's question
            
        Returns:
            Fallback prompt string
        """
        return f"""You are a helpful customer support assistant. A customer has asked a question, but the knowledge base is currently unavailable.

Customer Question: {question}

Please provide a polite response explaining that you're unable to access the information system at the moment, and suggest alternative ways for the customer to get help (such as contacting support directly or trying again later).

Answer:"""
    
    @staticmethod
    def build_clarification_prompt(
        question: str,
        context: str,
        similar_questions: List[str]
    ) -> str:
        """
        Build a prompt for clarifying ambiguous questions.
        
        Args:
            question: User's ambiguous question
            context: Available context
            similar_questions: List of similar questions from knowledge base
            
        Returns:
            Clarification prompt string
        """
        similar_q_text = "\n".join([f"- {q}" for q in similar_questions[:3]])
        
        return f"""A customer has asked a question that might relate to several topics. Help clarify what they're looking for.

Customer Question: {question}

Similar questions in our knowledge base:
{similar_q_text}

Available Information:
{context}

Provide a helpful response that either:
1. Answers the most likely interpretation of their question
2. Asks for clarification if the question is too ambiguous
3. Provides information on multiple related topics if appropriate

Answer:"""
    
    @staticmethod
    def extract_prompt_params(prompt_type: str = "default") -> Dict[str, float]:
        """
        Get recommended parameters for different prompt types.
        
        Args:
            prompt_type: Type of prompt (default, clarification, creative)
            
        Returns:
            Dictionary with temperature and max_tokens recommendations
        """
        params = {
            "default": {"temperature": 0.3, "max_tokens": 300},
            "clarification": {"temperature": 0.5, "max_tokens": 400},
            "creative": {"temperature": 0.7, "max_tokens": 500},
            "strict": {"temperature": 0.1, "max_tokens": 250}
        }
        
        return params.get(prompt_type, params["default"])