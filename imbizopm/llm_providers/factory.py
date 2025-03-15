"""
Factory function for creating LLM provider instances.
"""

from ..config import config
from .anthropic_provider import AnthropicProvider
from .base_provider import LLMProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider


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
