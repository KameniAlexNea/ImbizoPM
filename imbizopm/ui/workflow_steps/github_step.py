"""
GitHub integration step for the workflow UI.
"""

import json
from typing import Dict

import gradio as gr

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
        self.task_file = None
        self.task_json_input = None
        self.task_input_method = None
        self.load_task_btn = None

        # Initialize GitHub manager if token is available
        self.github_manager = None
        if self.github_token:
            try:
                self.github_manager = GitHubManager(token=self.github_token)
            except Exception as e:
                print(f"Failed to initialize GitHub manager: {e}")

    def _load_tasks_from_file(self, file) -> Dict:
        """Load tasks from an uploaded file."""
        if file is None:
            return {"success": False, "error": "No file uploaded"}

        try:
            with open(file.name, "r") as f:
                data = json.load(f)
            return {
                "success": True,
                "data": data,
                "message": f"Successfully loaded tasks from {file.name}",
            }
        except Exception as e:
            return {"success": False, "error": f"Error loading tasks: {str(e)}"}

    def _load_tasks_from_json(self, json_str: str) -> Dict:
        """Load tasks from a JSON string."""
        if not json_str or not json_str.strip():
            return {"success": False, "error": "No JSON input provided"}

        try:
            data = json.loads(json_str)
            return {
                "success": True,
                "data": data,
                "message": "Successfully parsed JSON input",
            }
        except Exception as e:
            return {"success": False, "error": f"Error parsing JSON: {str(e)}"}

    def _process_task_input(
        self, input_method: str, file, json_input: str, existing_tasks: Dict
    ) -> Dict:
        """Process task input from various sources based on selected method."""
        if existing_tasks and len(existing_tasks) > 0:
            return existing_tasks

        if input_method == "file_upload":
            result = self._load_tasks_from_file(file)
        elif input_method == "json_input":
            result = self._load_tasks_from_json(json_input)
        else:
            return {}

        if result.get("success", False):
            return result.get("data", {})
        return {}

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

            # Create project and ignore when it fails
            project_result = manager.create_project(
                repo_name=repo_name,
                project_name=tasks_data.get("project_title", "Project"),
                body=tasks_data.get("project_description", ""),
            )

            # Generate GitHub issues with the enhanced linking approach
            generator = ProjectGenerator("ollama")  # Provider doesn't matter here
            issues = generator.generate_github_issues(tasks_data)

            # Track parent-child relationship between issues
            issue_relationships = []
            parent_issues_map = {}  # Map parent titles to issue numbers
            subtask_issues_map = (
                {}
            )  # Map subtask titles to issue numbers and their parent titles

            # First pass: Create all issues and track their relationships
            created_issues = []
            for issue in issues:
                # Extract parent-child relationship from the body
                is_subtask = "Parent task:" in issue["body"]
                parent_title = None

                if is_subtask:
                    # Extract parent task title from body
                    for line in issue["body"].split("\n"):
                        if line.startswith("Parent task:"):
                            parent_title = line.replace("Parent task:", "").strip()
                            break

                # Create issue
                issue_result = manager.create_issue(
                    repo_name=repo_name,
                    title=issue["title"],
                    body=issue["body"],
                    labels=issue.get("labels", []),
                )

                if issue_result["success"]:
                    created_issue = issue_result["issue"]
                    created_issues.append(created_issue)

                    # Track this issue
                    if is_subtask and parent_title:
                        subtask_issues_map[issue["title"]] = {
                            "number": created_issue["number"],
                            "parent_title": parent_title,
                        }
                    else:
                        parent_issues_map[issue["title"]] = created_issue["number"]

            # Second pass: Create sub-issue relationships
            for subtask_title, subtask_info in subtask_issues_map.items():
                parent_title = subtask_info["parent_title"]

                if parent_title in parent_issues_map:
                    parent_number = parent_issues_map[parent_title]
                    child_number = subtask_info["number"]

                    # Create the sub-issue relationship
                    sub_issue_result = manager.create_sub_issue_relationship(
                        repo_name=repo_name,
                        parent_issue_number=parent_number,
                        child_issue_number=child_number,
                    )

                    if sub_issue_result["success"]:
                        issue_relationships.append(
                            {
                                "parent": parent_number,
                                "child": child_number,
                                "status": "linked",
                            }
                        )
                    else:
                        print(sub_issue_result.get("error"))
                        issue_relationships.append(
                            {
                                "parent": parent_number,
                                "child": child_number,
                                "status": "error",
                                "error": sub_issue_result.get("error"),
                            }
                        )

            return {
                "success": True,
                "repository": repo_result["repository"],
                "project": project_result,
                "issues_count": len(created_issues),
                "issues": created_issues,
                "relationships": issue_relationships,
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

        # Task data input section
        gr.Markdown("### Project Task Data")
        self.task_input_method = gr.Radio(
            choices=["file_upload", "json_input"],
            label="Task Input Method",
            value="file_upload",
        )

        # File upload option
        self.task_file = gr.File(
            label="Upload Tasks JSON File", visible=True, file_types=[".json"]
        )

        # Direct JSON input option
        self.task_json_input = gr.Textbox(
            label="Task Data JSON",
            placeholder='{"project_title": "My Project", "project_description": "Description", "tasks": [...]}',
            lines=10,
            visible=False,
        )

        # Add a submit button for task data
        self.load_task_btn = gr.Button("Load Task Data", variant="secondary")

        # GitHub repository settings
        gr.Markdown("### GitHub Repository Settings")
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
                self.project_private = gr.Checkbox(
                    label="Private Repository", value=False
                )
                self.create_project_btn = gr.Button(
                    "Create GitHub Project", variant="primary"
                )

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
        # Toggle visibility based on input method selection
        self.task_input_method.change(
            fn=self._toggle_input_visibility,
            inputs=[self.task_input_method],
            outputs=[self.task_file, self.task_json_input],
        )

        # Add handler for task data loading button
        self.load_task_btn.click(
            fn=self._load_task_data,
            inputs=[
                self.task_input_method,
                self.task_file,
                self.task_json_input,
                self.task_state,
            ],
            outputs=[self.github_result, self.task_state],
            queue=True,
        )

        # Create GitHub project with tasks
        self.create_project_btn.click(
            fn=self._handle_create_project,
            inputs=[
                self.task_state,
                self.project_repo_name,
                self.project_private,
                self.github_token,
            ],
            outputs=[self.github_result, self.task_state],
            queue=True,
        )

        # Finish workflow
        self.finish_btn.click(
            fn=lambda: "### Workflow Completed\n\nYour project has been created successfully!",
            outputs=[self.github_result],
        )

    def _toggle_input_visibility(self, input_method):
        """Toggle visibility of input elements based on selected method."""
        return (
            gr.Group(visible=input_method == "file_upload"),
            gr.Group(visible=input_method == "json_input"),
        )

    def _load_task_data(self, input_method, task_file, json_input, existing_tasks):
        """Handle loading task data from the selected source."""
        # Process task input from the selected method
        tasks_data = self._process_task_input(
            input_method, task_file, json_input, existing_tasks
        )

        if not tasks_data:
            result_message = (
                "### Failed to Load Task Data\n\nPlease check your input and try again."
            )
            return result_message, existing_tasks

        # Show success message with task details
        result_message = f"### Task Data Loaded Successfully\n\n"
        result_message += (
            f"- Project Title: {tasks_data.get('project_title', 'Not specified')}\n"
        )
        result_message += (
            f"- Description: {tasks_data.get('project_description', 'Not specified')}\n"
        )
        result_message += f"- Tasks: {len(tasks_data.get('tasks', []))} task(s) loaded"

        return result_message, tasks_data

    def _handle_create_project(self, tasks_data, repo_name, private, github_token):
        """Handle project creation with loaded task data."""
        if not tasks_data:
            result = {
                "success": False,
                "error": "No task data loaded. Please load task data first.",
            }
            return self._format_github_result(result), tasks_data

        # Create GitHub project with the tasks
        result = self._create_github_project_with_tasks(
            tasks_data, repo_name, private, github_token
        )

        return self._format_github_result(result), tasks_data
