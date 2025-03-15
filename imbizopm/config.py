"""
Configuration module for ImbizoPM.
"""

import os
from typing import Dict, Optional

from dotenv import load_dotenv


class Config:
    """Configuration class for ImbizoPM."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the configuration.
        
        Args:
            env_file: Path to .env file. If None, will look in default locations.
        """
        # Load environment variables
        load_dotenv(dotenv_path=env_file)
        
    @property
    def github_token(self) -> Optional[str]:
        """Get the GitHub token from environment."""
        return os.environ.get("GITHUB_TOKEN")
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get the OpenAI API key from environment."""
        return os.environ.get("OPENAI_API_KEY")
    
    @property
    def anthropic_api_key(self) -> Optional[str]:
        """Get the Anthropic API key from environment."""
        return os.environ.get("ANTHROPIC_API_KEY")
    
    @property
    def ollama_base_url(self) -> str:
        """Get the Ollama base URL from environment."""
        return os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    
    @property
    def ollama_model(self) -> str:
        """Get the Ollama model from environment."""
        return os.environ.get("OLLAMA_MODEL", "llama3")
    
    @property
    def openai_model(self) -> str:
        """Get the OpenAI model from environment."""
        return os.environ.get("OPENAI_MODEL", "gpt-4")
    
    @property
    def anthropic_model(self) -> str:
        """Get the Anthropic model from environment."""
        return os.environ.get("ANTHROPIC_MODEL", "claude-3-opus-20240229")
    
    def get_llm_config(self, provider: str) -> Dict:
        """
        Get configuration for a specific LLM provider.
        
        Args:
            provider: The provider name ('openai', 'anthropic', 'ollama')
            
        Returns:
            Dictionary with provider-specific configuration
        """
        if provider.lower() == "openai":
            return {
                "api_key": self.openai_api_key,
                "model": self.openai_model
            }
        elif provider.lower() == "anthropic":
            return {
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model
            }
        elif provider.lower() == "ollama":
            return {
                "base_url": self.ollama_base_url,
                "model": self.ollama_model
            }
        else:
            raise ValueError(f"Unsupported provider: {provider}")


# Create a global configuration instance
config = Config()
