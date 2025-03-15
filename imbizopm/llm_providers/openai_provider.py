"""
OpenAI provider implementation.
"""

import os
from typing import Iterator, Optional

from dotenv import load_dotenv
from openai import OpenAI

from .base_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI API provider for language model interactions."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key. If None, will look for OPENAI_API_KEY in environment
            model: The model to use, defaults to gpt-4
        """
        load_dotenv()
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using OpenAI API.

        Args:
            prompt: The prompt to send to the language model
            kwargs: Additional parameters like temperature, max_tokens, etc.

        Returns:
            Generated text response
        """
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    def generate_text_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream text generation using OpenAI API.

        Args:
            prompt: The prompt to send to the language model
            kwargs: Additional parameters like temperature, max_tokens, etc.

        Returns:
            Iterator yielding chunks of generated text
        """
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
