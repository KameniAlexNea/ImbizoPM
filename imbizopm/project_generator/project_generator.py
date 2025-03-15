"""
Project Generator module for creating project descriptions and task lists using LLMs.
"""

import json
import concurrent.futures
from typing import Dict, List, Tuple, Union, Optional

from ..llm_providers import LLMProvider, get_llm_provider
from .prompts import (
    project_description_prompt,
    project_refinement_prompt,
    tasks_generation_prompt,
    aggregation_prompt,
)


class ProjectGenerator:
    """Class for generating project descriptions and task lists using LLMs."""

    def __init__(self, llm_provider: Union[str, LLMProvider], **provider_kwargs):
        """
        Initialize the project generator.

        Args:
            llm_provider: Either a provider name ('openai', 'anthropic', 'ollama') or a LLMProvider instance
            provider_kwargs: Provider-specific configuration if a name is provided
        """
        if isinstance(llm_provider, str):
            self.llm = get_llm_provider(llm_provider, **provider_kwargs)
        else:
            self.llm = llm_provider

    def generate_project_description(self, project_prompt: str) -> str:
        """
        Generate a project description from a user prompt.

        Args:
            project_prompt: User's prompt describing the project idea

        Returns:
            Generated project description
        """
        prompt = project_description_prompt(project_prompt)
        return self.llm.generate_text(prompt)

    def refine_project_description(
        self, original_description: str, user_feedback: str
    ) -> str:
        """
        Refine the project description based on user feedback.

        Args:
            original_description: The original generated description
            user_feedback: User's feedback on how to improve the description

        Returns:
            Refined project description
        """
        prompt = project_refinement_prompt(original_description, user_feedback)
        return self.llm.generate_text(prompt)

    def generate_tasks(self, project_description: str) -> Dict:
        """
        Generate a list of tasks and subtasks for the project.

        Args:
            project_description: The finalized project description

        Returns:
            Dictionary containing project title, description, and a structured task list
        """
        prompt = tasks_generation_prompt(project_description)
        response = self.llm.generate_text(prompt)

        # Extract the JSON part (in case the LLM adds extra text)
        try:
            # Find the first '{' and the last '}'
            start_idx = response.find("{")
            end_idx = response.rfind("}")

            if start_idx == -1 or end_idx == -1:
                raise ValueError("No valid JSON found in the response")

            json_str = response[start_idx : end_idx + 1]
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If parsing fails, try to clean up the response
            clean_response = self._clean_json_response(response)
            return json.loads(clean_response)

    def _clean_json_response(self, response: str) -> str:
        """Clean up an LLM response to extract valid JSON."""
        # Find content between triple backticks if present
        import re

        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response)
        if json_match:
            return json_match.group(1)

        # Otherwise try to extract between the first { and last }
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        if start_idx >= 0 and end_idx >= 0:
            return response[start_idx : end_idx + 1]

        raise ValueError("Could not extract valid JSON from the LLM response")

    def generate_github_issues(self, tasks_data: Dict) -> List[Dict]:
        """
        Convert task data to GitHub issues format.

        Args:
            tasks_data: Dictionary with project tasks

        Returns:
            List of dictionaries with issue details
        """
        issues = []

        # Process main tasks
        for i, task in enumerate(tasks_data.get("tasks", [])):
            # Create issue for main task
            issue = {
                "title": task["title"],
                "body": f"{task['description']}\n\nComplexity: {task['complexity']}",
                "labels": task.get("labels", []),
            }
            issues.append(issue)

            # Process subtasks
            for subtask in task.get("subtasks", []):
                # Create issue for subtask
                sub_issue = {
                    "title": f"{task['title']} - {subtask['title']}",
                    "body": f"{subtask['description']}\n\nComplexity: {subtask['complexity']}\n\nParent task: {task['title']}",
                    "labels": subtask.get("labels", []),
                }
                issues.append(sub_issue)

        return issues

    def interactive_project_creation(
        self, initial_prompt: str
    ) -> Tuple[Dict, List[Dict]]:
        """
        Interactive process to create a project with description and tasks.

        Args:
            initial_prompt: User's initial project idea

        Returns:
            Tuple containing (project data, list of GitHub issues)
        """
        # Step 1: Generate initial project description
        print("\nGenerating initial project description...\n")
        description = self.generate_project_description(initial_prompt)
        print(f"\n{'-' * 40}\nGENERATED PROJECT DESCRIPTION:\n{'-' * 40}\n")
        print(description)

        # Step 2: Get user feedback and refine
        print(f"\n{'-' * 40}")
        feedback = input(
            "\nHow would you like to improve this description? (Press Enter to accept as is): "
        )

        if feedback.strip():
            print("\nRefining project description based on your feedback...\n")
            description = self.refine_project_description(description, feedback)
            print(f"\n{'-' * 40}\nREFINED PROJECT DESCRIPTION:\n{'-' * 40}\n")
            print(description)

        # Step 3: Generate tasks
        print("\nGenerating project tasks...\n")
        tasks_data = self.generate_tasks(description)

        # Print generated tasks
        print(f"\n{'-' * 40}\nPROJECT STRUCTURE:\n{'-' * 40}\n")
        print(f"Project: {tasks_data['project_title']}\n")

        for i, task in enumerate(tasks_data.get("tasks", []), 1):
            print(f"{i}. {task['title']} ({task['complexity']})")
            for j, subtask in enumerate(task.get("subtasks", []), 1):
                print(f"   {i}.{j} {subtask['title']} ({subtask['complexity']})")

        # Step 4: Confirm and generate GitHub issues
        print(f"\n{'-' * 40}")
        confirmation = input(
            "\nDo you want to create this project on GitHub? (yes/no): "
        )

        if confirmation.lower() in ("y", "yes"):
            issues = self.generate_github_issues(tasks_data)
            return tasks_data, issues
        else:
            return tasks_data, []
