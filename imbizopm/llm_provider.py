"""
LLM Provider module for interacting with different large language model APIs.
"""

import os
from abc import ABC, abstractmethod
from typing import Optional

import httpx
from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI

from .config import config


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
        self.client = httpx.Client(timeout=60.0)  # Longer timeout for local models

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

        data = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False,
        }

        response = self.client.post(f"{self.base_url}/api/generate", json=data)
        response.raise_for_status()

        return response.json()["response"]


def get_llm_provider(provider: str, **kwargs) -> LLMProvider:
    """
    Factory function to get an LLM provider instance.

    Args:
        provider: The provider name ('openai', 'anthropic', 'ollama')
        kwargs: Provider-specific configuration options

    Returns:
        An LLMProvider instance
    """
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }

    if provider.lower() not in providers:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    # If no kwargs provided, get from config
    if not kwargs:
        kwargs = config.get_llm_config(provider)

    provider_class = providers[provider.lower()]
    return provider_class(**kwargs)
