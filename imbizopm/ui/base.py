"""
Base UI components for ImbizoPM.
"""

from typing import Dict, List

import gradio as gr

from ..config import config


class BaseUI:
    """Base class for ImbizoPM UI components."""

    def __init__(self):
        """Initialize the base UI components."""
        # Configure theme
        self.theme = gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="blue",
        ).set(
            body_background_fill="*neutral_50",
            block_background_fill="*neutral_100",
            button_primary_background_fill="*primary_500",
            button_primary_background_fill_hover="*primary_600",
        )

        # Get available LLM providers based on environment variables
        self.available_providers = self._get_available_providers()

        # Initialize GitHub token
        self.github_token = config.github_token

    def _get_available_providers(self) -> List[str]:
        """Get the list of available LLM providers based on environment variables."""
        providers = []

        # Check for OpenAI API key
        if config.openai_api_key:
            providers.append("openai")

        # Check for Anthropic API key
        if config.anthropic_api_key:
            providers.append("anthropic")

        # Always add Ollama as it doesn't require API key (though may not be running)
        providers.append("ollama")

        return providers if providers else ["none"]

    def _format_tasks_for_display(self, tasks_data: Dict) -> str:
        """Format tasks data as a readable string for display."""
        if not tasks_data:
            return "No tasks generated."

        result = [
            f"# {tasks_data.get('project_title', 'Project')}\n",
            f"{tasks_data.get('project_description', '')}\n\n",
            "## Tasks\n",
        ]

        for i, task in enumerate(tasks_data.get("tasks", []), 1):
            result.append(f"### {i}. {task['title']} ({task['complexity']})\n")
            result.append(f"{task['description']}\n")
            result.append(f"Labels: {', '.join(task.get('labels', []))}\n")

            # Add subtasks if any
            if task.get("subtasks"):
                result.append("\nSubtasks:\n")
                for j, subtask in enumerate(task["subtasks"], 1):
                    result.append(
                        f"  {i}.{j} {subtask['title']} ({subtask['complexity']})\n"
                    )
                    result.append(f"  {subtask['description']}\n")
                    result.append(
                        f"  Labels: {', '.join(subtask.get('labels', []))}\n\n"
                    )
            result.append("\n")

        return "".join(result)

    def _format_github_result(self, result: Dict) -> str:
        """Format GitHub operation result as a readable string."""
        if not result:
            return "No result data."

        if not result.get("success"):
            return f"Error: {result.get('error', 'Unknown error')}"

        lines = ["## Operation Successful\n"]

        # Repository info
        if "repository" in result:
            repo = result["repository"]
            lines.append("### Repository\n")
            lines.append(f"- Name: {repo.get('name')}\n")
            if "full_name" in repo:
                lines.append(f"- Full Name: {repo.get('full_name')}\n")
            if "url" in repo:
                lines.append(f"- URL: {repo.get('url')}\n")
            lines.append("\n")

        # Project info
        if "project" in result and result["project"]["success"]:
            project = result["project"]["project"]
            lines.append("### Project\n")
            lines.append(f"- Name: {project.get('name')}\n")
            if "url" in project:
                lines.append(f"- URL: {project.get('url')}\n")
            if "columns" in project:
                lines.append(f"- Columns: {', '.join(project.get('columns'))}\n")
            lines.append("\n")

        # Issues info
        if "issues" in result:
            issues = result["issues"]
            lines.append(f"### Issues ({result.get('issues_count', len(issues))})\n")
            for i, issue in enumerate(issues[:10], 1):  # Limit to first 10 issues
                lines.append(f"{i}. {issue.get('title')} (#{issue.get('number')})\n")
                if "url" in issue:
                    lines.append(f"   URL: {issue.get('url')}\n")

            if len(issues) > 10:
                lines.append(f"\n... and {len(issues) - 10} more issues.\n")

        # Relationship info
        if "relationships" in result and result["relationships"]:
            relationships = result["relationships"]
            lines.append(f"\n### Issue Relationships ({len(relationships)})\n")
            success_count = sum(
                1 for rel in relationships if rel.get("status") == "linked"
            )
            lines.append(
                f"- Successfully linked: {success_count}/{len(relationships)}\n"
            )

            if success_count < len(relationships):
                lines.append(
                    "\nSome relationships could not be created. Check the GitHub interface.\n"
                )

        return "".join(lines)
