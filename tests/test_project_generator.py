"""
Tests for the project generator module.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from imbizopm.llm_providers import LLMProvider
from imbizopm.project_generator import ProjectGenerator


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def generate_text(self, prompt: str, **kwargs) -> str:
        """Return a mock response based on the prompt."""
        if "project description" in prompt.lower():
            return "# Task Manager App\n\nA web application for managing tasks and projects."
        elif "revise the project description" in prompt.lower():
            return "# Enhanced Task Manager App\n\nA web application for managing tasks and projects with team collaboration features."
        elif "create a structured list of tasks" in prompt.lower():
            return json.dumps(
                {
                    "project_title": "Task Manager App",
                    "project_description": "A web application for managing tasks and projects.",
                    "tasks": [
                        {
                            "title": "Setup project structure",
                            "description": "Initialize repository and create basic structure",
                            "complexity": "Low",
                            "labels": ["setup"],
                            "subtasks": [
                                {
                                    "title": "Create README",
                                    "description": "Add documentation",
                                    "complexity": "Low",
                                    "labels": ["documentation"],
                                }
                            ],
                        }
                    ],
                }
            )
        else:
            return "Mock response"

    def generate_text_stream(self, prompt: str, **kwargs):
        """Return a mock stream."""
        yield "Mock stream"


class TestProjectGenerator(unittest.TestCase):
    """Test cases for the project generator."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = MockLLMProvider()
        self.generator = ProjectGenerator(self.mock_llm)

    def test_generate_project_description(self):
        """Test generating a project description."""
        description = self.generator.generate_project_description(
            "Create a task manager app"
        )
        self.assertIn("Task Manager App", description)

    def test_refine_project_description(self):
        """Test refining a project description."""
        original = "# Task Manager App\n\nA web application for managing tasks."
        feedback = "Add team collaboration features."
        refined = self.generator.refine_project_description(original, feedback)
        self.assertIn("Enhanced", refined)
        self.assertIn("collaboration", refined)

    def test_generate_tasks(self):
        """Test generating tasks from a description."""
        description = "# Task Manager App\n\nA web application for managing tasks."
        tasks = self.generator.generate_tasks(description)
        self.assertEqual(tasks["project_title"], "Task Manager App")
        self.assertEqual(len(tasks["tasks"]), 1)
        self.assertEqual(len(tasks["tasks"][0]["subtasks"]), 1)

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

        # Test with nested JSON
        response = 'Here\'s the complex JSON:\n```\n{"outer": {"inner": "value"}}\n```'
        cleaned = self.generator._clean_json_response(response)
        self.assertEqual(cleaned, '{"outer": {"inner": "value"}}')

        # Test with invalid input (no JSON)
        with self.assertRaises(ValueError):
            self.generator._clean_json_response("No JSON here at all")

    def test_generate_github_issues(self):
        """Test generating GitHub issues from task data."""
        task_data = {
            "project_title": "Test Project",
            "project_description": "Test description",
            "tasks": [
                {
                    "title": "Main task",
                    "description": "Main task description",
                    "complexity": "Medium",
                    "labels": ["enhancement"],
                    "subtasks": [
                        {
                            "title": "Subtask",
                            "description": "Subtask description",
                            "complexity": "Low",
                            "labels": ["bug"],
                        }
                    ],
                }
            ],
        }

        issues = self.generator.generate_github_issues(task_data)
        self.assertEqual(len(issues), 2)  # 1 main task + 1 subtask
        self.assertEqual(issues[0]["title"], "Main task")
        self.assertEqual(issues[1]["title"], "Main task - Subtask")
        self.assertIn("enhancement", issues[0]["labels"])
        self.assertIn("bug", issues[1]["labels"])
        self.assertIn("Main task description", issues[0]["body"])
        self.assertIn("Complexity: Medium", issues[0]["body"])
        self.assertIn("Subtask description", issues[1]["body"])
        self.assertIn("Parent task: Main task", issues[1]["body"])

        # Test with multiple main tasks, no subtasks
        task_data = {
            "project_title": "Test Project",
            "project_description": "Test description",
            "tasks": [
                {
                    "title": "Task 1",
                    "description": "Task 1 description",
                    "complexity": "Low",
                    "labels": ["documentation"],
                },
                {
                    "title": "Task 2",
                    "description": "Task 2 description",
                    "complexity": "High",
                    "labels": ["bug"],
                },
            ],
        }

        issues = self.generator.generate_github_issues(task_data)
        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0]["title"], "Task 1")
        self.assertEqual(issues[1]["title"], "Task 2")
        self.assertIn("documentation", issues[0]["labels"])
        self.assertIn("bug", issues[1]["labels"])

        # Test with empty tasks array
        task_data = {
            "project_title": "Empty Project",
            "project_description": "No tasks",
            "tasks": [],
        }

        issues = self.generator.generate_github_issues(task_data)
        self.assertEqual(len(issues), 0)

    @patch("builtins.input", side_effect=["", "yes"])
    @patch("builtins.print")
    def test_interactive_project_creation(self, mock_print, mock_input):
        """Test interactive project creation."""
        project_data, issues = self.generator.interactive_project_creation(
            "Create a task manager"
        )
        self.assertEqual(project_data["project_title"], "Task Manager App")
        self.assertEqual(len(issues), 2)  # 1 main task + 1 subtask

    @patch("builtins.input", side_effect=["Add more features", "no"])
    @patch("builtins.print")
    def test_interactive_project_creation_with_feedback(self, mock_print, mock_input):
        """Test interactive project creation with feedback."""
        project_data, issues = self.generator.interactive_project_creation(
            "Create a task manager"
        )
        self.assertEqual(project_data["project_title"], "Task Manager App")
        self.assertEqual(len(issues), 0)  # User declined to create issues
        mock_input.assert_any_call(
            "\nHow would you like to improve this description? (Press Enter to accept as is): "
        )

    @patch("builtins.input", side_effect=["", "invalid"])
    @patch("builtins.print")
    def test_interactive_project_creation_invalid_confirmation(
        self, mock_print, mock_input
    ):
        """Test interactive project creation with invalid confirmation."""
        project_data, issues = self.generator.interactive_project_creation(
            "Create a task manager"
        )
        self.assertEqual(project_data["project_title"], "Task Manager App")
        self.assertEqual(len(issues), 0)  # Invalid confirmation treated as "no"

    @patch("imbizopm.llm_providers.get_llm_provider")
    def test_initialization_with_provider_name(self, mock_get_provider):
        """Test initialization with provider name."""
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider

        generator = ProjectGenerator("openai", api_key="test_key")

        mock_get_provider.assert_called_once_with("openai", api_key="test_key")
        self.assertEqual(generator.llm, mock_provider)


if __name__ == "__main__":
    unittest.main()
