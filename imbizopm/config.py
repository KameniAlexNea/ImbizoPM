"""
Configuration module for ImbizoPM.

This is the central configuration for the entire application. All modules should
import and use the 'config' instance from this module rather than creating their
own configuration objects.
"""

import os
from typing import Dict, Optional

from dotenv import load_dotenv

from .model_config import ModelConfigManager


class APIKeys:
    ollama_url = "http://localhost:11434"
    openai_key = ""
    anthropic_key = ""
    github_token = ""


class Config:
    """
    Configuration class for ImbizoPM.

    This is the main configuration class that provides access to all settings
    including environment variables and model configuration. The global 'config'
    instance at the bottom of this file should be used throughout the application.
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the configuration.

        Args:
            env_file: Path to .env file. If None, will look in default locations.
        """
        # Load environment variables
        load_dotenv(dotenv_path=env_file)

        # Initialize model configuration manager
        self.models = ModelConfigManager(env_file=env_file)

    @property
    def github_token(self) -> Optional[str]:
        """Get the GitHub token from environment."""
        return APIKeys.github_token or os.environ.get(
            "GITHUB_TOKEN",
        )

    @property
    def openai_api_key(self) -> Optional[str]:
        """Get the OpenAI API key from environment."""
        return APIKeys.openai_key or os.environ.get(
            "OPENAI_API_KEY",
        )

    @property
    def anthropic_api_key(self) -> Optional[str]:
        """Get the Anthropic API key from environment."""
        return APIKeys.anthropic_key or os.environ.get(
            "ANTHROPIC_API_KEY",
        )

    @property
    def ollama_base_url(self) -> str:
        """Get the Ollama base URL from environment."""
        return APIKeys.ollama_url or os.environ.get(
            "OLLAMA_BASE_URL",
        )

    @property
    def ollama_model(self) -> str:
        """Get the Ollama model from environment."""
        return self.models.ollama.default_model.name

    @property
    def openai_model(self) -> str:
        """Get the OpenAI model from environment."""
        return self.models.openai.default_model.name

    @property
    def anthropic_model(self) -> str:
        """Get the Anthropic model from environment."""
        return self.models.anthropic.default_model.name

    @property
    def master_provider(self) -> str:
        """Get the master provider for multi-provider operations."""
        return self.models.master_provider

    def get_llm_config(self, provider: str) -> Dict:
        """
        Get configuration for a specific LLM provider.

        Args:
            provider: The provider name ('openai', 'anthropic', 'ollama')

        Returns:
            Dictionary with provider-specific configuration
        """
        return self.models.get_llm_config(provider)


# Create a global configuration instance
# This is the single instance that should be imported and used throughout the application
config = Config()
