"""
Model configuration module for ImbizoPM.

This module provides configuration classes for different LLM providers and models.
It's designed to be used through the Config class in config.py, which creates a ModelConfigManager
instance and provides it through the 'models' attribute.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from dotenv import load_dotenv


@dataclass
class ModelInfo:
    """Information about a specific model."""

    name: str
    context_length: int = 8192
    is_default: bool = False
    capabilities: List[str] = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = ["text"]


class ProviderConfig:
    """Base class for provider configurations."""

    provider_name: str = "base"
    models: List[ModelInfo] = []
    base_url: Optional[str] = None

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @property
    def default_model(self) -> ModelInfo:
        """Get the default model for this provider."""
        for model in self.models:
            if model.is_default:
                return model
        return self.models[0] if self.models else None

    def get_config(self) -> Dict:
        """Get the configuration dictionary for this provider."""
        config = {"model": self.default_model.name if self.default_model else None}
        if self.api_key:
            config["api_key"] = self.api_key
        if self.base_url:
            config["base_url"] = self.base_url
        return config


class OpenAIConfig(ProviderConfig):
    """Configuration for OpenAI models."""

    provider_name = "openai"
    models = [
        ModelInfo(name="gpt-3.5-turbo", context_length=16385),
        ModelInfo(name="gpt-4", context_length=8192),
        ModelInfo(name="gpt-4-turbo", context_length=128000),
        ModelInfo(name="gpt-4o", context_length=128000, is_default=True),
    ]


class AnthropicConfig(ProviderConfig):
    """Configuration for Anthropic models."""

    provider_name = "anthropic"
    models = [
        ModelInfo(name="claude-3-haiku-20240307", context_length=200000),
        ModelInfo(name="claude-3-sonnet-20240229", context_length=200000),
        ModelInfo(
            name="claude-3-7-sonnet-20250219", context_length=200000, is_default=True
        ),
    ]


class OllamaConfig(ProviderConfig):
    """Configuration for Ollama models."""

    provider_name = "ollama"
    models = [
        ModelInfo(name="llama3", context_length=8192),
        ModelInfo(name="phi3", context_length=4096),
        ModelInfo(name="mistral", context_length=8192),
        ModelInfo(name="phi4", context_length=4096, is_default=True),
    ]

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = base_url or "http://localhost:11434"


class ModelConfigManager:
    """Manager class for all model configurations."""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the model configuration manager.

        Args:
            env_file: Path to .env file. If None, will look in default locations.
        """
        # Load environment variables
        load_dotenv(dotenv_path=env_file)

        # Initialize provider configs
        self.openai = OpenAIConfig(api_key=os.environ.get("OPENAI_API_KEY"))
        self.anthropic = AnthropicConfig(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.ollama = OllamaConfig(
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        )

        # Set default master provider
        self._master_provider = os.environ.get("MASTER_PROVIDER", "openai")

    @property
    def master_provider(self) -> str:
        """Get the master provider name."""
        return self._master_provider

    @master_provider.setter
    def master_provider(self, provider: str) -> None:
        """Set the master provider."""
        if provider in ["openai", "anthropic", "ollama"]:
            self._master_provider = provider
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def get_provider_config(self, provider: str) -> ProviderConfig:
        """
        Get the configuration for a specific provider.

        Args:
            provider: Provider name ('openai', 'anthropic', 'ollama')

        Returns:
            Provider configuration object
        """
        if provider.lower() == "openai":
            return self.openai
        elif provider.lower() == "anthropic":
            return self.anthropic
        elif provider.lower() == "ollama":
            return self.ollama
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def get_provider_model_names(self, provider: str) -> List[str]:
        """Get list of model names for a provider."""
        config = self.get_provider_config(provider)
        return [model.name for model in config.models]

    def get_llm_config(self, provider: str) -> Dict:
        """
        Get configuration dictionary for a specific LLM provider.

        Args:
            provider: The provider name ('openai', 'anthropic', 'ollama')

        Returns:
            Dictionary with provider-specific configuration
        """
        return self.get_provider_config(provider).get_config()
