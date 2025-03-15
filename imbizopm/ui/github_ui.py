"""
GitHub integration UI components for ImbizoPM.
"""

from typing import Dict

import gradio as gr

from ..github_manager import GitHubManager
from ..project_generator import ProjectGenerator
from .base import BaseUI


class GitHubUI(BaseUI):
    """UI components for GitHub integration."""

    def __init__(self):
        """Initialize the GitHub UI components."""
        super().__init__()

        # Initialize GitHub manager if token is available
        self.github_manager = None
        if self.github_token:
            try:
                self.github_manager = GitHubManager(token=self.github_token)
            except Exception as e:
                print(f"Failed to initialize GitHub manager: {e}")

    def _create_github_repository(
        self, repo_name: str, description: str, private: bool, github_token: str = None
    ) -> Dict:
        """
        Create a GitHub repository.
        """
        if not repo_name.strip():
            return {"success": False, "error": "Repository name is required"}

        try:
            # Use provided token or the one from initialization
            token = github_token or self.github_token
            if not token:
                return {"success": False, "error": "GitHub token is required"}

            # Initialize manager with the token
            manager = self.github_manager
            if not manager or github_token:
                manager = GitHubManager(token=token)

            # Create repository
            result = manager.create_repository(
                name=repo_name, description=description, private=private
            )

            return result
        except Exception as e:
            return {"success": False, "error": f"Error creating repository: {str(e)}"}

    def _create_github_project_with_tasks(
        self, tasks_data: Dict, repo_name: str, private: bool, github_token: str = None
    ) -> Dict:
        """
        Create a GitHub repository, project, and issues from task data.
        """
        if not tasks_data:
            return {"success": False, "error": "No task data provided"}

        if not repo_name.strip():
            # Generate repo name from project title
            repo_name = tasks_data.get("project_title", "").lower().replace(" ", "-")
            repo_name = "".join(c if c.isalnum() or c == "-" else "" for c in repo_name)

            if not repo_name:
                return {
                    "success": False,
                    "error": "Repository name could not be generated",
                }

        try:
            # Use provided token or the one from initialization
            token = github_token or self.github_token
            if not token:
                return {"success": False, "error": "GitHub token is required"}

            # Initialize manager with the token
            manager = self.github_manager
            if not manager or github_token:
                manager = GitHubManager(token=token)

            # Create repository
            repo_result = manager.create_repository(
                name=repo_name,
                description=tasks_data.get("project_description", ""),
                private=private,
            )

            if not repo_result["success"]:
                return repo_result

            # Create project board
            project_result = manager.create_project(
                repo_name=repo_name,
                project_name=tasks_data.get("project_title", "Project"),
                body=tasks_data.get("project_description", ""),
            )

            if not project_result["success"]:
                return project_result

            # Generate GitHub issues
            generator = ProjectGenerator("ollama")  # Provider doesn't matter here
            issues = generator.generate_github_issues(tasks_data)

            # Create issues
            created_issues = []
            for issue in issues:
                issue_result = manager.create_issue(
                    repo_name=repo_name,
                    title=issue["title"],
                    body=issue["body"],
                    labels=issue.get("labels", []),
                )

                if issue_result["success"]:
                    created_issues.append(issue_result["issue"])

            return {
                "success": True,
                "repository": repo_result["repository"],
                "project": project_result["project"],
                "issues_count": len(created_issues),
                "issues": created_issues,
            }

        except Exception as e:
            return {"success": False, "error": f"Error creating project: {str(e)}"}

    def build_ui(self) -> gr.Blocks:
        """Build the UI for GitHub integration."""
        with gr.Blocks(theme=self.theme) as github_ui:
            with gr.Row():
                with gr.Column(scale=1):
                    # Repository creation
                    gr.Markdown("### Create GitHub Repository")
                    github_token = gr.Textbox(
                        label="GitHub Token (optional if set in .env)", type="password"
                    )
                    repo_name = gr.Textbox(
                        label="Repository Name", placeholder="my-awesome-project"
                    )
                    repo_description = gr.Textbox(
                        label="Repository Description",
                        placeholder="A brief description of your project",
                    )
                    private = gr.Checkbox(label="Private Repository", value=False)
                    create_repo_btn = gr.Button("Create Repository", variant="primary")

                    # Full project creation with tasks
                    gr.Markdown("### Create Full Project with Tasks")
                    gr.Markdown(
                        "Use the tasks data from a JSON file or previous generation"
                    )
                    project_repo_name = gr.Textbox(
                        label="Repository Name (optional, generated from project title if empty)",
                        placeholder="project-name",
                    )
                    project_private = gr.Checkbox(
                        label="Private Repository", value=False
                    )

                    # Upload task data
                    task_file = gr.File(label="Upload Tasks JSON (optional)")

                    create_project_btn = gr.Button(
                        "Create Full Project", variant="primary"
                    )

                with gr.Column(scale=2):
                    github_result = gr.Markdown(label="GitHub Operation Result")

            # Task state for storing generated task data
            task_state = gr.State({})

            # Function to load JSON from file
            def load_tasks_from_file(file):
                if file is None:
                    return {}, "No file uploaded"

                try:
                    import json

                    with open(file.name, "r") as f:
                        data = json.load(f)
                    return data, f"Successfully loaded tasks from {file.name}"
                except Exception as e:
                    return {}, f"Error loading tasks: {str(e)}"

            # Set up event handlers
            create_repo_btn.click(
                fn=lambda name, desc, priv, token: self._format_github_result(
                    self._create_github_repository(name, desc, priv, token)
                ),
                inputs=[repo_name, repo_description, private, github_token],
                outputs=[github_result],
                queue=True,
            )

            # Load tasks from file
            task_file.change(
                fn=load_tasks_from_file,
                inputs=[task_file],
                outputs=[task_state, github_result],
            )

            create_project_btn.click(
                fn=lambda tasks, name, priv, token: self._format_github_result(
                    self._create_github_project_with_tasks(tasks, name, priv, token)
                ),
                inputs=[task_state, project_repo_name, project_private, github_token],
                outputs=[github_result],
                queue=True,
            )

        return github_ui
