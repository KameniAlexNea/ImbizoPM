"""
Ollama provider implementation for local LLMs.
"""

from typing import Iterator

import ollama

from .base_provider import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama provider for local language model interactions."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        """
        Initialize Ollama provider.

        Args:
            base_url: Base URL for the Ollama API, defaults to http://localhost:11434
            model: The model to use, defaults to llama3
        """
        self.base_url = base_url
        self.model = model
        self.client = ollama.Client(host=base_url)

    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using Ollama API.

        Args:
            prompt: The prompt to send to the language model
            kwargs: Additional parameters like temperature, etc.

        Returns:
            Generated text response
        """
        temperature = kwargs.get("temperature", 0.7)

        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            temperature=temperature,
            stream=False,
        )

        return response["response"]

    def generate_text_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream text generation using Ollama API.

        Args:
            prompt: The prompt to send to the language model
            kwargs: Additional parameters like temperature, etc.

        Returns:
            Iterator yielding chunks of generated text
        """
        temperature = kwargs.get("temperature", 0.7)

        for chunk in self.client.generate(
            model=self.model,
            prompt=prompt,
            temperature=temperature,
            stream=True,
        ):
            if "response" in chunk:
                yield chunk["response"]
