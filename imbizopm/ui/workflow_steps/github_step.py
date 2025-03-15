"""
GitHub integration step for the workflow UI.
"""

from typing import Dict

import gradio as gr

from ...config import config
from ...github_manager import GitHubManager
from ...project_generator import ProjectGenerator
from .base_step import BaseWorkflowStep


class GitHubStep(BaseWorkflowStep):
    """GitHub integration step."""
    
    def __init__(self):
        """Initialize the GitHub step."""
        super().__init__()
        # UI elements will be set during build_step
        self.github_token = None
        self.project_repo_name = None
        self.project_private = None
        self.create_project_btn = None
        self.github_result = None
        self.prev_btn = None
        self.finish_btn = None
        self.task_state = None
        
        # Initialize GitHub manager if token is available
        self.github_manager = None
        if self.github_token:
            try:
                self.github_manager = GitHubManager(token=self.github_token)
            except Exception as e:
                print(f"Failed to initialize GitHub manager: {e}")
                
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
            
    def build_step(self, visible: bool = False) -> None:
        """Build the UI for the GitHub integration step."""
        gr.Markdown("## Step 4: GitHub Integration")
        
        if not self.github_token:
            gr.Markdown(
                """
                ⚠️ **Warning**: GitHub token not found. Set GITHUB_TOKEN in your .env file 
                or provide a token below to create GitHub repositories.
                """
            )
        
        with gr.Row():
            with gr.Column(scale=1):
                self.github_token = gr.Textbox(
                    label="GitHub Token (optional if set in .env)",
                    type="password",
                )
                self.project_repo_name = gr.Textbox(
                    label="Repository Name",
                    placeholder="Leave empty to generate from project title",
                )
                self.project_private = gr.Checkbox(label="Private Repository", value=False)
                self.create_project_btn = gr.Button("Create GitHub Project", variant="primary")
            
            with gr.Column(scale=1):
                self.github_result = gr.Markdown(
                    label="GitHub Result",
                    value="GitHub operation results will appear here...",
                )
        
        # Task state for storing task data received from previous step
        self.task_state = gr.State({})
        
        # Navigation buttons
        with gr.Row():
            self.prev_btn = gr.Button("Back", variant="secondary")
            self.finish_btn = gr.Button("Finish Workflow", variant="secondary")
            
        # Register event handlers
        self.register_event_handlers()
    
    def register_event_handlers(self) -> None:
        """Register event handlers for this step's UI elements."""
        # Create GitHub project with tasks
        self.create_project_btn.click(
            fn=lambda tasks, name, priv, token: self._format_github_result(
                self._create_github_project_with_tasks(tasks, name, priv, token)
            ),
            inputs=[self.task_state, self.project_repo_name, self.project_private, self.github_token],
            outputs=[self.github_result],
            queue=True,
        )
        
        # Finish workflow
        self.finish_btn.click(
            fn=lambda: "### Workflow Completed\n\nYour project has been created successfully!",
            outputs=[self.github_result],
        )
