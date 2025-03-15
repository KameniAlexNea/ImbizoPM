"""
Tests for the LLM provider module.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from imbizopm.llm_provider import (AnthropicProvider, LLMProvider,
                                  OllamaProvider, OpenAIProvider,
                                  get_llm_provider)


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
        
        # Test with invalid provider
        with self.assertRaises(ValueError):
            get_llm_provider("invalid_provider")
    
    @patch('openai.OpenAI')
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
    
    @patch('anthropic.Anthropic')
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
    
    @patch('httpx.Client')
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
        self.assertEqual(data["model"], "llama3")


if __name__ == '__main__':
    unittest.main()
