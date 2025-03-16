"""
Ollama provider implementation for local LLMs.
"""

from typing import Iterator

import ollama

from .base_provider import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama provider for local language model interactions."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "phi4"):
        """
        Initialize Ollama provider.

        Args:
            base_url: Base URL for the Ollama API (default: "http://localhost:11434")
            model: The model to use (default: "phi4")
        """
        self.base_url = base_url
        self.model = model
        try:
            self.client = ollama.Client(host=base_url)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Ollama client: {str(e)}")

    def generate_text(self, prompt: str, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate text using Ollama API.

        Args:
            prompt: The prompt to send to the language model
            temperature: Controls randomness of output (default: 0.7)
            **kwargs: Additional parameters for the Ollama API

        Returns:
            Generated text response

        Raises:
            ValueError: If prompt is empty or invalid
            RuntimeError: If generation fails
        """
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": temperature},
                stream=False,
                **kwargs,
            )
            return response["response"]
        except Exception as e:
            raise RuntimeError(f"Failed to generate text: {str(e)}")

    def generate_text_stream(
        self, prompt: str, temperature: float = 0.7, **kwargs
    ) -> Iterator[str]:
        """
        Stream text generation using Ollama API.

        Args:
            prompt: The prompt to send to the language model
            temperature: Controls randomness of output (default: 0.7)
            **kwargs: Additional parameters for the Ollama API

        Yields:
            Chunks of generated text

        Raises:
            ValueError: If prompt is empty or invalid
            RuntimeError: If streaming fails
        """
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")

        try:
            stream = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": temperature},
                stream=True,
                **kwargs,
            )
            for chunk in stream:
                if "response" in chunk:
                    yield chunk["response"]
        except Exception as e:
            raise RuntimeError(f"Failed to stream text: {str(e)}")
