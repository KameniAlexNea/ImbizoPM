"""
Base class for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Iterator


class LLMProvider(ABC):
    """Abstract base class for language model providers."""

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text based on a prompt.

        Args:
            prompt: The prompt to send to the language model
            kwargs: Additional provider-specific parameters

        Returns:
            Generated text response
        """

    @abstractmethod
    def generate_text_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream generated text based on a prompt.

        Args:
            prompt: The prompt to send to the language model
            kwargs: Additional provider-specific parameters

        Returns:
            Iterator yielding chunks of generated text
        """
