"""
Unified workflow UI component for ImbizoPM.
"""

import json
from typing import Dict, List, Tuple, Union

import gradio as gr

from ..config import config
from ..github_manager import GitHubManager
from ..project_generator import MultiProviderProjectGenerator, ProjectGenerator
from .base import BaseUI


class WorkflowUI(BaseUI):
    """UI component for the unified project workflow."""

    def __init__(self):
        """Initialize the workflow UI component."""
        super().__init__()

        # Initialize GitHub manager if token is available
        self.github_manager = None
        if self.github_token:
            try:
                self.github_manager = GitHubManager(token=self.github_token)
            except Exception as e:
                print(f"Failed to initialize GitHub manager: {e}")
    
    def _generate_project_description(
        self, project_idea: str, provider: str, model: str = None
    ) -> str:
        """
        Generate a project description using the specified LLM provider.
        """
        if provider == "none" or not project_idea.strip():
            return "Please select a provider and enter a project idea."

        try:
            # Get provider configuration
            provider_kwargs = config.get_llm_config(provider)
            if model and model.strip():
                provider_kwargs["model"] = model

            # Initialize project generator
            generator = ProjectGenerator(provider, **provider_kwargs)

            # Generate description
            return generator.generate_project_description(project_idea)

        except Exception as e:
            return f"Error generating project description: {str(e)}"

    def _multi_provider_generate(
        self,
        project_idea: str,
        use_openai: bool,
        use_anthropic: bool,
        use_ollama: bool,
        master_provider: str,
    ) -> str:
        """
        Generate a project description using multiple providers.
        """
        if not project_idea.strip():
            return "Please enter a project idea."

        # Build list of providers to use
        providers = []
        provider_kwargs = []

        if use_openai and "openai" in self.available_providers:
            providers.append("openai")
            provider_kwargs.append(config.get_llm_config("openai"))

        if use_anthropic and "anthropic" in self.available_providers:
            providers.append("anthropic")
            provider_kwargs.append(config.get_llm_config("anthropic"))

        if use_ollama and "ollama" in self.available_providers:
            providers.append("ollama")
            provider_kwargs.append(config.get_llm_config("ollama"))

        if not providers:
            return "Please select at least one provider."

        # Determine master provider index
        try:
            master_idx = providers.index(master_provider)
        except ValueError:
            master_idx = 0  # Default to first provider if specified master isn't used

        try:
            # Initialize multi-provider generator
            generator = MultiProviderProjectGenerator(
                providers=providers,
                provider_kwargs=provider_kwargs,
                master_provider_idx=master_idx,
            )

            # Generate description
            return generator.generate_project_description(project_idea)

        except Exception as e:
            return f"Error generating project description: {str(e)}"

    def _refine_project_description(
        self, original_description: str, feedback: str, provider: str, model: str = None
    ) -> str:
        """
        Refine a project description based on feedback.
        """
        if (
            provider == "none"
            or not original_description.strip()
            or not feedback.strip()
        ):
            return "Please provide both a description and feedback."

        try:
            # Get provider configuration
            provider_kwargs = config.get_llm_config(provider)
            if model and model.strip():
                provider_kwargs["model"] = model

            # Initialize project generator
            generator = ProjectGenerator(provider, **provider_kwargs)

            # Refine description
            return generator.refine_project_description(original_description, feedback)

        except Exception as e:
            return f"Error refining project description: {str(e)}"

    def _generate_project_tasks(
        self, project_description: str, provider: str, model: str = None
    ) -> Tuple[str, Dict]:
        """
        Generate project tasks based on a description.
        """
        if provider == "none" or not project_description.strip():
            return "Please select a provider and enter a project description.", {}

        try:
            # Get provider configuration
            provider_kwargs = config.get_llm_config(provider)
            if model and model.strip():
                provider_kwargs["model"] = model

            # Initialize project generator
            generator = ProjectGenerator(provider, **provider_kwargs)

            # Generate tasks
            tasks_data = generator.generate_tasks(project_description)

            # Format tasks for display
            formatted_tasks = self._format_tasks_for_display(tasks_data)

            return formatted_tasks, tasks_data

        except Exception as e:
            return f"Error generating project tasks: {str(e)}", {}

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

    def _export_tasks_to_json(self, tasks_data: Dict, filename: str) -> str:
        """
        Export tasks data to a JSON file.
        """
        if not tasks_data:
            return "No task data to export."

        if not filename.strip():
            return "Please provide a filename."

        try:
            # Ensure filename has .json extension
            if not filename.lower().endswith(".json"):
                filename += ".json"

            with open(filename, "w") as f:
                json.dump(tasks_data, f, indent=2)

            return f"Tasks successfully exported to {filename}"

        except Exception as e:
            return f"Error exporting tasks: {str(e)}"

    def build_ui(self) -> gr.Blocks:
        """Build the unified workflow UI."""
        with gr.Blocks(theme=self.theme) as workflow_ui:
            current_step = gr.State(1)
            project_data = gr.State({})
            task_data = gr.State({})

            # Step 1: Project Idea
            with gr.Group(visible=True) as step1_group:
                gr.Markdown("## Step 1: Project Idea")
                with gr.Row():
                    with gr.Column(scale=1):
                        project_idea = gr.Textbox(
                            label="Project Idea",
                            placeholder="Enter a brief description of your project idea",
                            lines=5,
                        )
                        
                        with gr.Accordion("Configuration", open=False):
                            # Single provider options
                            with gr.Group():
                                use_single_provider = gr.Checkbox(
                                    label="Use Single Provider", value=True
                                )
                                provider = gr.Dropdown(
                                    choices=self.available_providers,
                                    label="LLM Provider",
                                    value=(
                                        self.available_providers[0]
                                        if self.available_providers
                                        else "none"
                                    ),
                                    visible=True,
                                )
                                model = gr.Textbox(
                                    label="Model (optional)",
                                    placeholder="Leave blank for default model",
                                    visible=True,
                                )
                            
                            # Multi-provider options
                            with gr.Group(visible=False) as multi_provider_options:
                                gr.Markdown("#### Providers to Use")
                                with gr.Row():
                                    use_openai = gr.Checkbox(
                                        label="OpenAI",
                                        value="openai" in self.available_providers,
                                        interactive="openai" in self.available_providers,
                                    )
                                    use_anthropic = gr.Checkbox(
                                        label="Anthropic",
                                        value="anthropic" in self.available_providers,
                                        interactive="anthropic" in self.available_providers,
                                    )
                                    use_ollama = gr.Checkbox(
                                        label="Ollama",
                                        value="ollama" in self.available_providers,
                                        interactive="ollama" in self.available_providers,
                                    )

                                master_provider = gr.Dropdown(
                                    choices=[p for p in self.available_providers if p != "none"],
                                    label="Master Provider (for aggregation)",
                                    value=(
                                        self.available_providers[0]
                                        if self.available_providers
                                        and self.available_providers[0] != "none"
                                        else None
                                    ),
                                )
                        
                        generate_btn = gr.Button("Generate Project Description", variant="primary")

                    with gr.Column(scale=1):
                        project_description = gr.Markdown(
                            label="Generated Description",
                            value="Project description will appear here...",
                        )
                
                # Navigation buttons
                with gr.Row():
                    step1_next_btn = gr.Button("Next: Task Generation", variant="secondary", interactive=False)

            # Step 2: Project Review & Refinement
            with gr.Group(visible=False) as step2_group:
                gr.Markdown("## Step 2: Project Review & Refinement")
                with gr.Row():
                    with gr.Column(scale=1):
                        current_description = gr.Markdown(label="Current Description")
                        feedback = gr.Textbox(
                            label="Feedback for Improvement",
                            placeholder="What would you like to improve or add to the description?",
                            lines=3,
                        )
                        refine_btn = gr.Button("Refine Description", variant="primary")
                        
                    with gr.Column(scale=1):
                        refined_description = gr.Markdown(
                            label="Refined Description",
                            value="Refined description will appear here...",
                        )
                
                # Navigation buttons
                with gr.Row():
                    step2_prev_btn = gr.Button("Back", variant="secondary")
                    step2_skip_btn = gr.Button("Skip Refinement", variant="secondary")
                    step2_next_btn = gr.Button("Accept & Generate Tasks", variant="primary")

            # Step 3: Task Generation
            with gr.Group(visible=False) as step3_group:
                gr.Markdown("## Step 3: Task Generation")
                with gr.Row():
                    with gr.Column(scale=1):
                        final_description = gr.Markdown(label="Project Description")
                        
                        with gr.Accordion("Task Generation Options", open=False):
                            task_provider = gr.Dropdown(
                                choices=self.available_providers,
                                label="LLM Provider",
                                value=(
                                    self.available_providers[0]
                                    if self.available_providers
                                    else "none"
                                ),
                            )
                            task_model = gr.Textbox(
                                label="Model (optional)",
                                placeholder="Leave blank for default model",
                            )
                        
                        generate_tasks_btn = gr.Button("Generate Tasks", variant="primary")
                        
                    with gr.Column(scale=1):
                        tasks_display = gr.Markdown(
                            label="Generated Tasks",
                            value="Tasks will appear here...",
                        )
                
                # Export option
                with gr.Row():
                    export_filename = gr.Textbox(
                        label="Export to JSON",
                        placeholder="tasks.json",
                        value="tasks.json",
                    )
                    export_btn = gr.Button("Export", variant="secondary")
                
                # Navigation buttons
                with gr.Row():
                    step3_prev_btn = gr.Button("Back", variant="secondary")
                    step3_next_btn = gr.Button("Next: GitHub Integration", variant="secondary", interactive=False)

            # Step 4: GitHub Integration
            with gr.Group(visible=False) as step4_group:
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
                        github_token = gr.Textbox(
                            label="GitHub Token (optional if set in .env)",
                            type="password",
                        )
                        project_repo_name = gr.Textbox(
                            label="Repository Name",
                            placeholder="Leave empty to generate from project title",
                        )
                        project_private = gr.Checkbox(label="Private Repository", value=False)
                        create_project_btn = gr.Button("Create GitHub Project", variant="primary")
                    
                    with gr.Column(scale=1):
                        github_result = gr.Markdown(
                            label="GitHub Result",
                            value="GitHub operation results will appear here...",
                        )
                
                # Navigation buttons
                with gr.Row():
                    step4_prev_btn = gr.Button("Back", variant="secondary")
                    step4_finish_btn = gr.Button("Finish Workflow", variant="secondary")

            # Define functions for UI interactions
            def toggle_provider_options(use_single):
                return (
                    gr.Group(visible=use_single),  # Single provider options
                    gr.Group(visible=not use_single),  # Multi-provider options
                )

            def update_visibility(step):
                return {
                    1: (
                        gr.Group(visible=True),   # step1_group
                        gr.Group(visible=False),  # step2_group
                        gr.Group(visible=False),  # step3_group
                        gr.Group(visible=False),  # step4_group
                    ),
                    2: (
                        gr.Group(visible=False),  # step1_group
                        gr.Group(visible=True),   # step2_group
                        gr.Group(visible=False),  # step3_group
                        gr.Group(visible=False),  # step4_group
                    ),
                    3: (
                        gr.Group(visible=False),  # step1_group
                        gr.Group(visible=False),  # step2_group
                        gr.Group(visible=True),   # step3_group
                        gr.Group(visible=False),  # step4_group
                    ),
                    4: (
                        gr.Group(visible=False),  # step1_group
                        gr.Group(visible=False),  # step2_group
                        gr.Group(visible=False),  # step3_group
                        gr.Group(visible=True),   # step4_group
                    ),
                }[step]

            def generate_description(idea, use_single, prov, mod, use_oa, use_an, use_ol, master_prov):
                if use_single:
                    return self._generate_project_description(idea, prov, mod)
                else:
                    return self._multi_provider_generate(idea, use_oa, use_an, use_ol, master_prov)
                
            def enable_next_button(description):
                # Check if description is not empty and not an error message
                valid = (
                    description 
                    and description != "Project description will appear here..."
                    and not description.startswith("Error")
                    and not description.startswith("Please select")
                )
                return gr.Button(interactive=valid)

            def prepare_for_step2(desc, step):
                # Store the description and update UI
                return desc, step + 1, desc

            def prepare_for_step3(desc, step, is_refined=False):
                # Use either the refined or original description
                description = desc if is_refined else desc
                return step + 1, description

            def generate_tasks(description, provider, model):
                formatted_tasks, tasks = self._generate_project_tasks(description, provider, model)
                return formatted_tasks, tasks, gr.Button(interactive=True) if tasks else gr.Button(interactive=False)

            # Set up event handlers
            use_single_provider.change(
                fn=toggle_provider_options,
                inputs=[use_single_provider],
                outputs=[gr.Group(), multi_provider_options],
            )

            # Step 1 events
            generate_btn.click(
                fn=generate_description,
                inputs=[
                    project_idea, 
                    use_single_provider, 
                    provider, 
                    model, 
                    use_openai, 
                    use_anthropic, 
                    use_ollama, 
                    master_provider
                ],
                outputs=[project_description],
                queue=True,
            ).then(
                fn=enable_next_button,
                inputs=[project_description],
                outputs=[step1_next_btn],
            )

            step1_next_btn.click(
                fn=prepare_for_step2,
                inputs=[project_description, current_step],
                outputs=[project_data, current_step, current_description],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            # Step 2 events
            refine_btn.click(
                fn=self._refine_project_description,
                inputs=[current_description, feedback, provider, model],
                outputs=[refined_description],
                queue=True,
            )

            step2_prev_btn.click(
                fn=lambda step: step - 1,
                inputs=[current_step],
                outputs=[current_step],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            step2_skip_btn.click(
                fn=prepare_for_step3,
                inputs=[project_data, current_step, gr.Checkbox(value=False)],
                outputs=[current_step, final_description],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            step2_next_btn.click(
                fn=prepare_for_step3,
                inputs=[refined_description, current_step, gr.Checkbox(value=True)],
                outputs=[current_step, final_description],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            # Step 3 events
            generate_tasks_btn.click(
                fn=generate_tasks,
                inputs=[final_description, task_provider, task_model],
                outputs=[tasks_display, task_data, step3_next_btn],
                queue=True,
            )

            export_btn.click(
                fn=self._export_tasks_to_json,
                inputs=[task_data, export_filename],
                outputs=[tasks_display],
            )

            step3_prev_btn.click(
                fn=lambda step: step - 1,
                inputs=[current_step],
                outputs=[current_step],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            step3_next_btn.click(
                fn=lambda step: step + 1,
                inputs=[current_step],
                outputs=[current_step],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            # Step 4 events
            create_project_btn.click(
                fn=lambda tasks, name, priv, token: self._format_github_result(
                    self._create_github_project_with_tasks(tasks, name, priv, token)
                ),
                inputs=[task_data, project_repo_name, project_private, github_token],
                outputs=[github_result],
                queue=True,
            )

            step4_prev_btn.click(
                fn=lambda step: step - 1,
                inputs=[current_step],
                outputs=[current_step],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            step4_finish_btn.click(
                fn=lambda: gr.Markdown(
                    value="### Workflow Completed\n\nYour project has been created successfully!"
                ),
                outputs=[github_result],
            )

        return workflow_ui
