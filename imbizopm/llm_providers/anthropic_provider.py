"""
Anthropic provider implementation.
"""

import os
from typing import Iterator, Optional

from anthropic import Anthropic
from dotenv import load_dotenv

from .base_provider import LLMProvider


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider for language model interactions."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key. If None, will look for ANTHROPIC_API_KEY in environment
            model: The model to use, defaults to claude-3-opus
        """
        load_dotenv()
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using Anthropic API.

        Args:
            prompt: The prompt to send to the language model
            kwargs: Additional parameters like temperature, max_tokens, etc.

        Returns:
            Generated text response
        """
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)

        response = self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.content[0].text

    def generate_text_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream text generation using Anthropic API.

        Args:
            prompt: The prompt to send to the language model
            kwargs: Additional parameters like temperature, max_tokens, etc.

        Returns:
            Iterator yielding chunks of generated text
        """
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)

        with self.client.messages.stream(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        ) as stream:
            for text in stream.text_stream:
                yield text
