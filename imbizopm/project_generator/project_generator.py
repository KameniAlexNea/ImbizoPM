"""
Project Generator module for creating project descriptions and task lists using LLMs.
"""

from typing import Dict, List, Tuple, Union

from ..llm_providers import LLMProvider, get_llm_provider
from ..utilities.parser import parse_json
from .prompts import (
    project_description_prompt,
    project_refinement_prompt,
    tasks_generation_prompt,
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

    def generate_project_description(self, project_prompt: str):
        """
        Generate a project description from a user prompt.

        Args:
            project_prompt: User's prompt describing the project idea

        Returns:
            Generated project description
        """
        prompt = project_description_prompt(project_prompt)
        yield from self.llm.generate_text_stream(prompt)

    def refine_project_description(self, original_description: str, user_feedback: str):
        """
        Refine the project description based on user feedback.

        Args:
            original_description: The original generated description
            user_feedback: User's feedback on how to improve the description

        Returns:
            Refined project description
        """
        prompt = project_refinement_prompt(original_description, user_feedback)
        yield from self.llm.generate_text_stream(prompt)

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
        text = parse_json(response)
        if not text:
            raise ValueError("No valid JSON found in the LLM response")
        return text

    def generate_github_issues(self, tasks_data: Dict) -> List[Dict]:
        """
        Convert task data to GitHub issues format with parent-child relationships.

        Args:
            tasks_data: Dictionary with project tasks

        Returns:
            List of dictionaries with issue details including linking information
        """
        issues = []
        task_index = {}  # Keep track of task indices for linking

        # Process main tasks first
        for i, task in enumerate(tasks_data.get("tasks", [])):
            # Create unique reference ID for the task
            task_ref = f"task_{i+1}"

            # Create issue for main task
            issue = {
                "title": task["title"],
                "body": f"{task['description']}\n\nComplexity: {task['complexity']}",
                "labels": task.get("labels", []),
                "ref_id": task_ref,
                "is_subtask": False,
                "children": [],  # Will store refs to child tasks
            }
            issues.append(issue)
            task_index[task_ref] = len(issues) - 1

            # Keep track of subtask references
            for j, subtask in enumerate(task.get("subtasks", [])):
                subtask_ref = f"subtask_{i+1}_{j+1}"
                # Record this subtask as child of the current task
                issue["children"].append(subtask_ref)

                # Create issue for subtask
                sub_issue = {
                    "title": f"{task['title']} - {subtask['title']}",
                    "body": f"{subtask['description']}\n\nComplexity: {subtask['complexity']}",
                    "labels": subtask.get("labels", []),
                    "ref_id": subtask_ref,
                    "is_subtask": True,
                    "parent": task_ref,  # Reference to parent task
                }
                issues.append(sub_issue)
                task_index[subtask_ref] = len(issues) - 1

        # Now that we have all the issues, update their descriptions to include links
        for i, issue in enumerate(issues):
            if issue["is_subtask"]:
                # Add parent reference to subtask
                parent_idx = task_index[issue["parent"]]
                parent_title = issues[parent_idx]["title"]
                issue["body"] += f"\n\nParent task: {parent_title}"

            if "children" in issue and issue["children"]:
                # Add subtask references to parent task
                issue["body"] += "\n\nSubtasks:"
                for child_ref in issue["children"]:
                    child_idx = task_index[child_ref]
                    child_title = issues[child_idx]["title"]
                    issue["body"] += f"\n- {child_title}"

            # Clean up the temporary linking fields before returning
            for field in ["ref_id", "is_subtask", "children", "parent"]:
                if field in issue:
                    del issue[field]

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
