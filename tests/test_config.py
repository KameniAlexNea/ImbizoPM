"""
Tests for the configuration module.
"""

import os
import unittest
from unittest.mock import patch

from imbizopm.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for the configuration class."""

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_github_token"})
    def test_github_token(self):
        """Test getting GitHub token from environment."""
        config = Config()
        self.assertEqual(config.github_token, "test_github_token")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_openai_key"})
    def test_openai_api_key(self):
        """Test getting OpenAI API key from environment."""
        config = Config()
        self.assertEqual(config.openai_api_key, "test_openai_key")

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_anthropic_key"})
    def test_anthropic_api_key(self):
        """Test getting Anthropic API key from environment."""
        config = Config()
        self.assertEqual(config.anthropic_api_key, "test_anthropic_key")

    @patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://custom-ollama:1234"})
    def test_ollama_base_url(self):
        """Test getting Ollama base URL from environment."""
        config = Config()
        self.assertEqual(config.ollama_base_url, "http://custom-ollama:1234")

    def test_ollama_base_url_default(self):
        """Test default Ollama base URL."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            self.assertEqual(config.ollama_base_url, "http://localhost:11434")

    @patch.dict(os.environ, {"OLLAMA_MODEL": "llama2"})
    def test_ollama_model(self):
        """Test getting Ollama model from environment."""
        config = Config()
        self.assertEqual(config.ollama_model, "llama2")

    def test_ollama_model_default(self):
        """Test default Ollama model."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            self.assertEqual(config.ollama_model, "phi4")

    @patch.dict(os.environ, {"OPENAI_MODEL": "gpt-3.5-turbo"})
    def test_openai_model(self):
        """Test getting OpenAI model from environment."""
        config = Config()
        self.assertEqual(config.openai_model, "gpt-3.5-turbo")

    def test_openai_model_default(self):
        """Test default OpenAI model."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            self.assertEqual(config.openai_model, "gpt-4")

    @patch.dict(os.environ, {"ANTHROPIC_MODEL": "claude-3-sonnet"})
    def test_anthropic_model(self):
        """Test getting Anthropic model from environment."""
        config = Config()
        self.assertEqual(config.anthropic_model, "claude-3-sonnet")

    def test_anthropic_model_default(self):
        """Test default Anthropic model."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            self.assertEqual(config.anthropic_model, "claude-3-opus-20240229")

    @patch.dict(
        os.environ, {"OPENAI_API_KEY": "test_openai_key", "OPENAI_MODEL": "gpt-4-turbo"}
    )
    def test_get_llm_config_openai(self):
        """Test getting OpenAI configuration."""
        config = Config()
        llm_config = config.get_llm_config("openai")

        self.assertEqual(llm_config["api_key"], "test_openai_key")
        self.assertEqual(llm_config["model"], "gpt-4-turbo")

    @patch.dict(
        os.environ,
        {
            "ANTHROPIC_API_KEY": "test_anthropic_key",
            "ANTHROPIC_MODEL": "claude-3-haiku",
        },
    )
    def test_get_llm_config_anthropic(self):
        """Test getting Anthropic configuration."""
        config = Config()
        llm_config = config.get_llm_config("anthropic")

        self.assertEqual(llm_config["api_key"], "test_anthropic_key")
        self.assertEqual(llm_config["model"], "claude-3-haiku")

    @patch.dict(
        os.environ, {"OLLAMA_BASE_URL": "http://custom:1234", "OLLAMA_MODEL": "mistral"}
    )
    def test_get_llm_config_ollama(self):
        """Test getting Ollama configuration."""
        config = Config()
        llm_config = config.get_llm_config("ollama")

        self.assertEqual(llm_config["base_url"], "http://custom:1234")
        self.assertEqual(llm_config["model"], "mistral")

    def test_get_llm_config_invalid(self):
        """Test getting configuration for invalid provider."""
        config = Config()
        with self.assertRaises(ValueError):
            config.get_llm_config("invalid_provider")


if __name__ == "__main__":
    unittest.main()
