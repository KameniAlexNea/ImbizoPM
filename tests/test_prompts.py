"""
Tests for the prompts module.
"""

import unittest

from imbizopm.project_generator.prompts import (
    aggregation_prompt,
    project_description_prompt,
    project_refinement_prompt,
    tasks_generation_prompt,
)


class TestPrompts(unittest.TestCase):
    """Test cases for the prompts module."""

    def test_project_description_prompt(self):
        """Test the project description prompt template."""
        prompt = project_description_prompt("Create a web blog")

        # Check that the prompt contains the project idea
        self.assertIn("Create a web blog", prompt)
        self.assertIn("generate a comprehensive project description", prompt.lower())

        # Check that template sections are included
        self.assertIn("project title", prompt.lower())
        self.assertIn("project overview", prompt.lower())
        self.assertIn("main features", prompt.lower())
        self.assertIn("technology stack", prompt.lower())

    def test_project_refinement_prompt(self):
        """Test the project refinement prompt template."""
        original = "# Blog\n\nA simple blog website"
        feedback = "Add user authentication"

        prompt = project_refinement_prompt(original, feedback)

        # Check that the prompt contains both the original description and feedback
        self.assertIn("# Blog", prompt)
        self.assertIn("A simple blog website", prompt)
        self.assertIn("Add user authentication", prompt)

        # Check instruction is included
        self.assertIn("revise the project description", prompt.lower())

    def test_tasks_generation_prompt(self):
        """Test the tasks generation prompt template."""
        description = "# Task Manager\n\nA task management application"

        prompt = tasks_generation_prompt(description)

        # Check that the prompt contains the project description
        self.assertIn("# Task Manager", prompt)
        self.assertIn("A task management application", prompt)

        # Check that template instructions are included
        self.assertIn("create a structured list of tasks", prompt.lower())
        self.assertIn("hierarchical structure", prompt.lower())
        self.assertIn("estimated complexity", prompt.lower())
        self.assertIn("labels for github issues", prompt.lower())

        # Check that output format instructions are included
        self.assertIn("Format your response as a JSON", prompt)
        self.assertIn("project_title", prompt)
        self.assertIn("tasks", prompt)
        self.assertIn("subtasks", prompt)

    def test_aggregation_prompt(self):
        """Test the aggregation prompt template."""
        descriptions = ["# Blog 1\n\nDescription 1", "# Blog 2\n\nDescription 2"]
        original = "Create a blog website"

        prompt = aggregation_prompt(descriptions, original)

        # Check that the prompt contains all descriptions and the original prompt
        self.assertIn("Create a blog website", prompt)
        self.assertIn("Description 1", prompt)
        self.assertIn("Description 2", prompt)
        self.assertIn("# Blog 1", prompt)
        self.assertIn("# Blog 2", prompt)

        # Check instruction is included
        self.assertIn("combines the best elements", prompt.lower())
        self.assertIn("comprehensive project description", prompt.lower())


if __name__ == "__main__":
    unittest.main()
