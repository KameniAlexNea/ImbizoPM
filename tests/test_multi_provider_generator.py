"""
Tests for the multi-provider project generator module.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from imbizopm.llm_providers import LLMProvider
from imbizopm.project_generator import MultiProviderProjectGenerator


class MockProvider1(LLMProvider):
    """First mock LLM provider for testing."""

    def generate_text(self, prompt: str, **kwargs) -> str:
        """Return a mock response based on the prompt."""
        if "project description" in prompt.lower():
            return "# Task Manager App\n\nA web application for managing tasks with team features."
        elif "task" in prompt.lower():
            return json.dumps(
                {
                    "project_title": "Task Manager App",
                    "project_description": "A web application for managing tasks.",
                    "tasks": [
                        {
                            "title": "Setup project",
                            "description": "Initialize repository",
                            "complexity": "Low",
                            "labels": ["setup"],
                            "subtasks": [],
                        }
                    ],
                }
            )
        return "Provider 1 response"

    def generate_text_stream(self, prompt: str, **kwargs):
        """Return a mock stream."""
        yield "Provider 1 stream"


class MockProvider2(LLMProvider):
    """Second mock LLM provider for testing."""

    def generate_text(self, prompt: str, **kwargs) -> str:
        """Return a mock response based on the prompt."""
        if "project description" in prompt.lower():
            return "# Advanced Task Manager\n\nA collaborative task management system with reports."
        elif "task" in prompt.lower():
            return json.dumps(
                {
                    "project_title": "Advanced Task Manager",
                    "project_description": "A collaborative task management system.",
                    "tasks": [
                        {
                            "title": "Implement authentication",
                            "description": "User login/signup",
                            "complexity": "Medium",
                            "labels": ["auth"],
                            "subtasks": [],
                        }
                    ],
                }
            )
        elif "multiple project descriptions" in prompt.lower():
            return "# Unified Task Manager\n\nA comprehensive task management solution."
        elif "multiple task lists" in prompt.lower():
            return json.dumps(
                {
                    "project_title": "Unified Task Manager",
                    "project_description": "A comprehensive task management solution.",
                    "tasks": [
                        {
                            "title": "Setup project",
                            "description": "Initialize repository",
                            "complexity": "Low",
                            "labels": ["setup"],
                            "subtasks": [],
                        },
                        {
                            "title": "Implement authentication",
                            "description": "User login/signup",
                            "complexity": "Medium",
                            "labels": ["auth"],
                            "subtasks": [],
                        },
                    ],
                }
            )
        return "Provider 2 response"

    def generate_text_stream(self, prompt: str, **kwargs):
        """Return a mock stream."""
        yield "Provider 2 stream"


class TestMultiProviderGenerator(unittest.TestCase):
    """Test cases for the multi-provider project generator."""

    def setUp(self):
        """Set up test fixtures."""
        self.provider1 = MockProvider1()
        self.provider2 = MockProvider2()
        self.generator = MultiProviderProjectGenerator(
            providers=[self.provider1, self.provider2],
            master_provider_idx=1,  # Use provider2 as master
        )

    def test_initialization(self):
        """Test initialization with different providers."""
        # Test with provider instances
        generator = MultiProviderProjectGenerator(
            providers=[self.provider1, self.provider2]
        )
        self.assertEqual(len(generator.llm_providers), 2)
        self.assertIs(
            generator.llm, generator.llm_providers[0]
        )  # Default master is first

        # Test with invalid master index
        with self.assertRaises(ValueError):
            MultiProviderProjectGenerator(
                providers=[self.provider1, self.provider2], master_provider_idx=5
            )

        # Test with provider kwargs mismatch
        with self.assertRaises(ValueError):
            MultiProviderProjectGenerator(
                providers=["openai", "anthropic", "ollama"],
                provider_kwargs=[
                    {"api_key": "key1"}
                ],  # Only one config for three providers
            )

    @patch("imbizopm.llm_providers.get_llm_provider")
    def test_initialization_with_provider_names(self, mock_get_provider):
        """Test initialization with provider names."""
        mock_get_provider.side_effect = [self.provider1, self.provider2]

        generator = MultiProviderProjectGenerator(
            providers=["openai", "anthropic"],
            provider_kwargs=[{"api_key": "key1"}, {"api_key": "key2"}],
        )

        self.assertEqual(len(generator.llm_providers), 2)
        mock_get_provider.assert_any_call("openai", api_key="key1")
        mock_get_provider.assert_any_call("anthropic", api_key="key2")

    def test_generate_project_description_with_single_provider(self):
        """Test project description generation with only one valid provider."""
        # Create a generator with only one provider
        generator = MultiProviderProjectGenerator(providers=[self.provider1])

        description = generator.generate_project_description("Create a task manager")
        self.assertIn("Task Manager App", description)
        self.assertNotIn(
            "_aggregate_descriptions", description
        )  # No aggregation with single provider

    def test_generate_project_description_with_multiple_providers(self):
        """Test project description generation with multiple providers."""
        description = self.generator.generate_project_description(
            "Create a task manager"
        )

        # Should use the master provider (provider2) to aggregate descriptions
        self.assertIn("Unified Task Manager", description)

    def test_generate_tasks_with_single_provider(self):
        """Test task generation with only one valid provider."""
        # Create a generator with only one provider
        generator = MultiProviderProjectGenerator(providers=[self.provider1])

        tasks = generator.generate_tasks("# Task Manager App")
        self.assertEqual(tasks["project_title"], "Task Manager App")
        self.assertEqual(len(tasks["tasks"]), 1)
        self.assertEqual(tasks["tasks"][0]["title"], "Setup project")

    def test_generate_tasks_with_multiple_providers(self):
        """Test task generation with multiple providers."""
        tasks = self.generator.generate_tasks("# Task Manager App")

        # Should aggregate tasks using master provider
        self.assertEqual(tasks["project_title"], "Unified Task Manager")
        self.assertEqual(len(tasks["tasks"]), 2)
        self.assertEqual(tasks["tasks"][0]["title"], "Setup project")
        self.assertEqual(tasks["tasks"][1]["title"], "Implement authentication")

    @patch("concurrent.futures.ThreadPoolExecutor")
    def test_parallel_generate(self, mock_executor_class):
        """Test parallel text generation from multiple providers."""
        # Setup mock executor
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor

        # Setup mock futures
        mock_future1 = MagicMock()
        mock_future1.result.return_value = "Result 1"

        mock_future2 = MagicMock()
        mock_future2.result.return_value = "Result 2"

        mock_executor.submit.side_effect = [mock_future1, mock_future2]
        mock_executor_class.as_completed.return_value = [mock_future1, mock_future2]

        # Call _parallel_generate
        with patch(
            "concurrent.futures.as_completed", return_value=[mock_future1, mock_future2]
        ):
            results = self.generator._parallel_generate(["Prompt 1", "Prompt 2"])

        self.assertEqual(results, ["Result 1", "Result 2"])
        mock_executor.submit.assert_any_call(self.provider1.generate_text, "Prompt 1")
        mock_executor.submit.assert_any_call(self.provider2.generate_text, "Prompt 2")

    def test_clean_json_response(self):
        """Test JSON response cleaning function."""
        # Test with code blocks
        response = 'Here\'s the JSON:\n```json\n{"key": "value"}\n```'
        cleaned = self.generator._clean_json_response(response)
        self.assertEqual(cleaned, '{"key": "value"}')

        # Test with direct JSON
        response = 'Some text before {"key": "value"} some text after'
        cleaned = self.generator._clean_json_response(response)
        self.assertEqual(cleaned, '{"key": "value"}')

        # Test with invalid response
        response = "This is not JSON at all"
        with self.assertRaises(ValueError):
            self.generator._clean_json_response(response)

    def test_aggregate_descriptions(self):
        """Test aggregating descriptions from multiple providers."""
        descriptions = [
            "# Description 1\nThis is the first description.",
            "# Description 2\nThis is the second description.",
        ]

        result = self.generator._aggregate_descriptions(descriptions, "original prompt")
        self.assertIn("Unified Task Manager", result)

        # Test with only one description
        result = self.generator._aggregate_descriptions(
            ["Single description"], "prompt"
        )
        self.assertEqual(result, "Single description")

        # Test with empty descriptions
        with self.assertRaises(ValueError):
            self.generator._aggregate_descriptions([], "prompt")

        with self.assertRaises(ValueError):
            self.generator._aggregate_descriptions(["", "  "], "prompt")

    def test_aggregate_tasks(self):
        """Test aggregating task lists from multiple providers."""
        task_lists = [
            {
                "project_title": "Project 1",
                "tasks": [{"title": "Task 1", "description": "Description 1"}],
            },
            {
                "project_title": "Project 2",
                "tasks": [{"title": "Task 2", "description": "Description 2"}],
            },
        ]

        result = self.generator._aggregate_tasks(task_lists, "project description")
        self.assertEqual(result["project_title"], "Unified Task Manager")
        self.assertEqual(len(result["tasks"]), 2)

        # Test with only one task list
        result = self.generator._aggregate_tasks([task_lists[0]], "project description")
        self.assertEqual(result, task_lists[0])

        # Test with empty task lists
        with self.assertRaises(ValueError):
            self.generator._aggregate_tasks([], "project description")

        with self.assertRaises(ValueError):
            self.generator._aggregate_tasks(
                [{"project_title": "Empty", "tasks": []}], "description"
            )


if __name__ == "__main__":
    unittest.main()
