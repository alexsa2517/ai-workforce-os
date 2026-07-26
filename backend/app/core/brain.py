"""
AI Brain - Central intelligence and reasoning module

The Brain is the core cognitive component that processes inputs,
manages context, and coordinates responses across AI services.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from app.services.llm.factory import LLMFactory
from app.core.config import settings

logger = logging.getLogger("ai_workforce.brain")


class Brain:
    """
    Central AI Brain for the AI Workforce OS.

    Responsible for:
    - Processing incoming messages
    - Managing conversation context and memory
    - Routing requests to appropriate AI services
    - Maintaining agent state and personality
    - Coordinating multi-agent workflows
    """

    def __init__(self, provider: str = "openai"):
        """
        Initialize the Brain with default settings.

        Args:
            provider: Default LLM provider to use
        """
        self.provider = provider
        self.context: List[Dict[str, str]] = []
        self.system_prompt: str = (
            "You are an AI Employee in the AI Workforce OS system. "
            "You are professional, helpful, and capable of handling various tasks. "
            "Always respond in the same language as the user."
        )
        self.max_context_length: int = 50
        logger.info(f"Brain initialized with provider: {provider}")

    def process(self, message: str, context: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Process an incoming message and generate a response.

        Args:
            message: User message to process
            context: Optional conversation context history

        Returns:
            Dictionary with input, response, and metadata
        """
        logger.info(f"Processing message (length: {len(message)})")

        # Update context
        if context:
            self.context = context
        self.context.append({"role": "user", "content": message})

        # Truncate context if too long
        if len(self.context) > self.max_context_length:
            self.context = self.context[-self.max_context_length:]

        # Generate response
        try:
            llm = LLMFactory.get(self.provider)
            response = llm.generate(
                message=message,
                system_prompt=self.system_prompt,
                context=self.context,
            )
        except Exception as e:
            logger.error(f"Brain processing error: {e}")
            response = f"I apologize, but I encountered an error processing your request: {str(e)}"

        # Add response to context
        self.context.append({"role": "assistant", "content": response})

        return {
            "input": message,
            "response": response,
            "provider": self.provider,
            "context_length": len(self.context),
        }

    def set_personality(self, personality: str) -> None:
        """
        Set the AI's personality and system prompt.

        Args:
            personality: Description of the desired personality
        """
        self.system_prompt = personality
        logger.info("Personality updated")

    def set_provider(self, provider: str) -> None:
        """
        Switch the LLM provider.

        Args:
            provider: New provider name
        """
        self.provider = provider
        logger.info(f"Provider switched to: {provider}")

    def clear_context(self) -> None:
        """Clear conversation history."""
        self.context = []
        logger.info("Context cleared")

    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current conversation context.

        Returns:
            Context summary with metadata
        """
        return {
            "total_messages": len(self.context),
            "provider": self.provider,
            "system_prompt_length": len(self.system_prompt),
            "last_user_message": self.context[-1]["content"] if self.context and self.context[-1]["role"] == "user" else None,
        }

    def analyze_task(self, message: str) -> Dict[str, Any]:
        """
        Analyze a task request and determine the best course of action.

        Args:
            message: Task description

        Returns:
            Analysis result with task type, priority, and suggested action
        """
        task_keywords = {
            "create": {"type": "creation", "priority": 3},
            "analyze": {"type": "analysis", "priority": 2},
            "report": {"type": "reporting", "priority": 2},
            "search": {"type": "research", "priority": 3},
            "schedule": {"type": "scheduling", "priority": 4},
            "meeting": {"type": "coordination", "priority": 4},
            "email": {"type": "communication", "priority": 3},
            "data": {"type": "data_processing", "priority": 2},
        }

        message_lower = message.lower()
        for keyword, task_info in task_keywords.items():
            if keyword in message_lower:
                return {
                    "detected_task": task_info["type"],
                    "priority": task_info["priority"],
                    "confidence": 0.8,
                    "suggested_action": f"Process as {task_info['type']} task",
                }

        return {
            "detected_task": "general",
            "priority": 1,
            "confidence": 0.5,
            "suggested_action": "Process as general inquiry",
        }
