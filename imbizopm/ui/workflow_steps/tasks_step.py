"""
Task generation step for the workflow UI.
"""

import json
from typing import Dict, Tuple

import gradio as gr

from ...config import config
from ...project_generator import ProjectGenerator
from .base_step import BaseWorkflowStep


class TasksStep(BaseWorkflowStep):
    """Project task generation step."""

    def __init__(self):
        """Initialize the tasks step."""
        super().__init__()
        # UI elements will be set during build_step
        self.final_description = None
        self.task_provider = None
        self.task_model = None
        self.generate_btn = None
        self.tasks_display = None
        self.task_state = None
        self.export_filename = None
        self.export_btn = None
        self.prev_btn = None
        self.next_btn = None

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

            # Generate tasks with streaming
            tasks_data = generator.generate_tasks(project_description)

            # Format tasks for display
            formatted_tasks = self._format_tasks_for_display(tasks_data)

            return formatted_tasks, tasks_data

        except Exception as e:
            return f"Error generating project tasks: {str(e)}", {}

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

    def build_step(self, visible: bool = False) -> None:
        """Build the UI for the task generation step."""
        gr.Markdown("## Step 3: Task Generation")

        with gr.Row():
            with gr.Column(scale=1):
                self.final_description = gr.Markdown(label="Project Description")

                with gr.Accordion("Task Generation Options", open=False):
                    self.task_provider = gr.Dropdown(
                        choices=self.available_providers,
                        label="LLM Provider",
                        value=(
                            self.available_providers[0]
                            if self.available_providers
                            else "none"
                        ),
                    )
                    self.task_model = gr.Textbox(
                        label="Model (optional)",
                        placeholder="Leave blank for default model",
                    )

                self.generate_btn = gr.Button("Generate Tasks", variant="primary")

            with gr.Column(scale=1):
                self.tasks_display = gr.Markdown(
                    label="Generated Tasks",
                    value="Tasks will appear here...",
                )

        # Task state for storing generated task data
        self.task_state = gr.State({})

        # Export option
        with gr.Row():
            self.export_filename = gr.Textbox(
                label="Export to JSON",
                placeholder="tasks.json",
                value="tasks.json",
            )
            self.export_btn = gr.Button("Export", variant="secondary")

        # Navigation buttons
        with gr.Row():
            self.prev_btn = gr.Button("Back", variant="secondary")
            self.next_btn = gr.Button(
                "Next: GitHub Integration", variant="secondary", interactive=False
            )

        # Register event handlers
        self.register_event_handlers()

    def register_event_handlers(self) -> None:
        """Register event handlers for this step's UI elements."""
        # Generate tasks
        self.generate_btn.click(
            fn=self._generate_project_tasks,
            inputs=[self.final_description, self.task_provider, self.task_model],
            outputs=[self.tasks_display, self.task_state],
            queue=True,
        ).then(
            fn=lambda tasks: gr.Button(interactive=bool(tasks)),
            inputs=[self.task_state],
            outputs=[self.next_btn],
        )

        # Export tasks
        self.export_btn.click(
            fn=self._export_tasks_to_json,
            inputs=[self.task_state, self.export_filename],
            outputs=[self.tasks_display],
        )
