"""
Tests for the project generator module.
"""

import json
import unittest
from unittest.mock import patch

from imbizopm.llm_provider import LLMProvider
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

    @patch("builtins.input", side_effect=["", "yes"])
    @patch("builtins.print")
    def test_interactive_project_creation(self, mock_print, mock_input):
        """Test interactive project creation."""
        project_data, issues = self.generator.interactive_project_creation(
            "Create a task manager"
        )
        self.assertEqual(project_data["project_title"], "Task Manager App")
        self.assertEqual(len(issues), 2)  # 1 main task + 1 subtask


if __name__ == "__main__":
    unittest.main()
