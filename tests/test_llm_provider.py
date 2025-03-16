"""
Tests for the LLM provider module.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from imbizopm.llm_providers import (
    AnthropicProvider,
    OllamaProvider,
    OpenAIProvider,
    get_llm_provider,
)


class TestLLMProvider(unittest.TestCase):
    """Test cases for the LLM provider classes."""

    def test_get_llm_provider_factory(self):
        """Test the provider factory function."""
        # Test with valid providers
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = get_llm_provider("openai")
            self.assertIsInstance(provider, OpenAIProvider)

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            provider = get_llm_provider("anthropic")
            self.assertIsInstance(provider, AnthropicProvider)

        # Test with Ollama (no env needed)
        provider = get_llm_provider("ollama")
        self.assertIsInstance(provider, OllamaProvider)

        # Test with invalid provider
        with self.assertRaises(ValueError):
            get_llm_provider("invalid_provider")

    def test_get_llm_provider_with_kwargs(self):
        """Test the provider factory function with kwargs."""
        # Test with custom API key
        provider = get_llm_provider("openai", api_key="custom_key")
        self.assertIsInstance(provider, OpenAIProvider)
        self.assertEqual(provider.api_key, "custom_key")

        # Test with custom model
        provider = get_llm_provider(
            "anthropic", api_key="test_key", model="claude-3-haiku"
        )
        self.assertIsInstance(provider, AnthropicProvider)
        self.assertEqual(provider.model, "claude-3-haiku")

        # Test with custom Ollama settings
        provider = get_llm_provider(
            "ollama", base_url="http://example.com", model="custom-model"
        )
        self.assertIsInstance(provider, OllamaProvider)
        self.assertEqual(provider.base_url, "http://example.com")
        self.assertEqual(provider.model, "custom-model")

    @patch("openai.OpenAI")
    def test_openai_provider(self, mock_openai):
        """Test OpenAI provider."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"

        mock_client.chat.completions.create.return_value = mock_response

        # Test with API key
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = OpenAIProvider()
            result = provider.generate_text("Test prompt")

            self.assertEqual(result, "Generated text")
            mock_client.chat.completions.create.assert_called_once()

            # Verify the call arguments
            call_args = mock_client.chat.completions.create.call_args[1]
            self.assertEqual(call_args["model"], "gpt-4")
            self.assertEqual(call_args["messages"][0]["content"], "Test prompt")

        # Test with custom model and parameters
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = OpenAIProvider(model="gpt-3.5-turbo")
            result = provider.generate_text(
                "Test prompt", temperature=0.5, max_tokens=500
            )

            call_args = mock_client.chat.completions.create.call_args[1]
            self.assertEqual(call_args["model"], "gpt-3.5-turbo")
            self.assertEqual(call_args["temperature"], 0.5)
            self.assertEqual(call_args["max_tokens"], 500)

    @patch("openai.OpenAI")
    def test_openai_provider_stream(self, mock_openai):
        """Test OpenAI provider streaming."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Create mock chunks
        chunk1 = MagicMock()
        chunk1.choices = [MagicMock()]
        chunk1.choices[0].delta.content = "First"

        chunk2 = MagicMock()
        chunk2.choices = [MagicMock()]
        chunk2.choices[0].delta.content = " chunk"

        chunk3 = MagicMock()
        chunk3.choices = [MagicMock()]
        chunk3.choices[0].delta.content = ""  # Empty content to test filtering

        mock_client.chat.completions.create.return_value = [chunk1, chunk2, chunk3]

        # Test streaming
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = OpenAIProvider()
            chunks = list(provider.generate_text_stream("Test prompt"))

            self.assertEqual(chunks, ["First", " chunk"])

            # Verify streaming was requested
            call_args = mock_client.chat.completions.create.call_args[1]
            self.assertTrue(call_args["stream"])

    @patch("openai.OpenAI")
    def test_openai_provider_error_handling(self, mock_openai):
        """Test OpenAI provider error handling."""
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API error")

        # Test error handling
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = OpenAIProvider()
            with self.assertRaises(Exception):
                provider.generate_text("Test prompt")

        # Test error handling in stream
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = OpenAIProvider()
            with self.assertRaises(Exception):
                list(provider.generate_text_stream("Test prompt"))

    @patch("anthropic.Anthropic")
    def test_anthropic_provider(self, mock_anthropic):
        """Test Anthropic provider."""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Generated text"

        mock_client.messages.create.return_value = mock_response

        # Test with API key
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            provider = AnthropicProvider()
            result = provider.generate_text("Test prompt")

            self.assertEqual(result, "Generated text")
            mock_client.messages.create.assert_called_once()

            # Verify the call arguments
            call_args = mock_client.messages.create.call_args[1]
            self.assertTrue("claude-3" in call_args["model"])
            self.assertEqual(call_args["messages"][0]["content"], "Test prompt")

        # Test with missing API key
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                AnthropicProvider()

    @patch("anthropic.Anthropic")
    def test_anthropic_provider_stream(self, mock_anthropic):
        """Test Anthropic provider streaming."""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        # Mock the context manager for streaming
        mock_stream = MagicMock()
        mock_client.messages.stream.return_value.__enter__.return_value = mock_stream
        mock_stream.text_stream = [
            "First",
            " chunk",
            "",
        ]  # Include empty chunk for testing

        # Test streaming
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            provider = AnthropicProvider()
            chunks = list(provider.generate_text_stream("Test prompt"))

            self.assertEqual(chunks, ["First", " chunk", ""])

            # Verify the call arguments
            mock_client.messages.stream.assert_called_once()
            call_args = mock_client.messages.stream.call_args[1]
            self.assertTrue("claude-3" in call_args["model"])
            self.assertEqual(call_args["messages"][0]["content"], "Test prompt")

    @patch("anthropic.Anthropic")
    def test_anthropic_provider_error_handling(self, mock_anthropic):
        """Test Anthropic provider error handling."""
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API error")

        # Test error handling
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            provider = AnthropicProvider()
            with self.assertRaises(Exception):
                provider.generate_text("Test prompt")

    @patch("httpx.Client")
    def test_ollama_provider(self, mock_client_class):
        """Test Ollama provider."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Generated text"}
        mock_client.post.return_value = mock_response

        # Test the provider
        provider = OllamaProvider()
        result = provider.generate_text("Test prompt")

        self.assertEqual(result, "Generated text")
        mock_client.post.assert_called_once()

        # Verify the call arguments
        url = mock_client.post.call_args[0][0]
        data = mock_client.post.call_args[1]["json"]
        self.assertEqual(url, "http://localhost:11434/api/generate")
        self.assertEqual(data["prompt"], "Test prompt")
        self.assertEqual(data["model"], "phi4")

    @patch("ollama.Client")
    def test_ollama_provider_with_custom_params(self, mock_client_class):
        """Test Ollama provider with custom parameters."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = {"response": "Generated text"}
        mock_client.generate.return_value = mock_response

        # Test with custom URL and model
        provider = OllamaProvider(base_url="http://example.com:1234", model="mistral")
        result = provider.generate_text("Test prompt", temperature=0.3)

        mock_client_class.assert_called_once_with(host="http://example.com:1234")
        mock_client.generate.assert_called_once()

        # Verify call arguments
        call_args = mock_client.generate.call_args[1]
        self.assertEqual(call_args["model"], "mistral")
        self.assertEqual(call_args["prompt"], "Test prompt")
        self.assertEqual(call_args["temperature"], 0.3)
        self.assertFalse(call_args["stream"])

    @patch("ollama.Client")
    def test_ollama_provider_stream(self, mock_client_class):
        """Test Ollama provider streaming."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Create mock chunks
        chunks = [
            {"response": "First"},
            {"response": " chunk"},
            {},  # Empty chunk to test filtering
        ]
        mock_client.generate.return_value = chunks

        # Test streaming
        provider = OllamaProvider()
        result = list(provider.generate_text_stream("Test prompt"))

        self.assertEqual(result, ["First", " chunk"])

        # Verify streaming was requested
        call_args = mock_client.generate.call_args[1]
        self.assertTrue(call_args["stream"])

    @patch("ollama.Client")
    def test_ollama_provider_error_handling(self, mock_client_class):
        """Test Ollama provider error handling."""
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.generate.side_effect = Exception("Connection error")

        # Test error handling
        provider = OllamaProvider()
        with self.assertRaises(Exception):
            provider.generate_text("Test prompt")

        # Test error handling in stream
        with self.assertRaises(Exception):
            list(provider.generate_text_stream("Test prompt"))


if __name__ == "__main__":
    unittest.main()
