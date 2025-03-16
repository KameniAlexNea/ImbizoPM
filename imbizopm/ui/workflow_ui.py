"""
Unified workflow UI component for ImbizoPM.
"""

import gradio as gr

from .base import BaseUI
from .workflow_steps.description_step import DescriptionStep
from .workflow_steps.github_step import GitHubStep
from .workflow_steps.refinement_step import RefinementStep
from .workflow_steps.tasks_step import TasksStep


class WorkflowUI(BaseUI):
    """UI component for the unified project workflow."""

    def __init__(self):
        """Initialize the workflow UI component."""
        super().__init__()

        # Initialize step components
        self.description_step = DescriptionStep()
        self.refinement_step = RefinementStep()
        self.tasks_step = TasksStep()
        self.github_step = GitHubStep()

    def build_ui(self) -> gr.Blocks:
        """Build the unified workflow UI."""
        with gr.Blocks(theme=self.theme) as workflow_ui:
            # State variables for workflow
            current_step = gr.State(1)
            project_data = gr.State({})
            task_data = gr.State({})

            # Step 1: Project Description Generation
            with gr.Group(visible=True) as step1_group:
                self.description_step.build_step(visible=True)

            # Step 2: Project Refinement
            with gr.Group(visible=False) as step2_group:
                self.refinement_step.build_step()

            # Step 3: Task Generation
            with gr.Group(visible=False) as step3_group:
                self.tasks_step.build_step()

            # Step 4: GitHub Integration
            with gr.Group(visible=False) as step4_group:
                self.github_step.build_step()

            # Define function to update step visibility
            def update_visibility(step):
                return {
                    1: (
                        gr.Group(visible=True),  # step1_group
                        gr.Group(visible=False),  # step2_group
                        gr.Group(visible=False),  # step3_group
                        gr.Group(visible=False),  # step4_group
                    ),
                    2: (
                        gr.Group(visible=False),  # step1_group
                        gr.Group(visible=True),  # step2_group
                        gr.Group(visible=False),  # step3_group
                        gr.Group(visible=False),  # step4_group
                    ),
                    3: (
                        gr.Group(visible=False),  # step1_group
                        gr.Group(visible=False),  # step2_group
                        gr.Group(visible=True),  # step3_group
                        gr.Group(visible=False),  # step4_group
                    ),
                    4: (
                        gr.Group(visible=False),  # step1_group
                        gr.Group(visible=False),  # step2_group
                        gr.Group(visible=False),  # step3_group
                        gr.Group(visible=True),  # step4_group
                    ),
                }[step]

            # Connect the workflow steps with navigation handlers

            # Step 1 navigation
            self.description_step.next_btn.click(
                fn=lambda desc, step: (desc, step + 1, desc),
                inputs=[self.description_step.project_description, current_step],
                outputs=[
                    project_data,
                    current_step,
                    self.refinement_step.current_description,
                ],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            # Step 2 navigation
            self.refinement_step.prev_btn.click(
                fn=lambda step: step - 1,
                inputs=[current_step],
                outputs=[current_step],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            self.refinement_step.skip_btn.click(
                fn=lambda desc, step: (step + 1, desc),
                inputs=[project_data, current_step],
                outputs=[current_step, self.tasks_step.final_description],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            self.refinement_step.next_btn.click(
                fn=lambda desc, step: (step + 1, desc),
                inputs=[self.refinement_step.refined_description, current_step],
                outputs=[current_step, self.tasks_step.final_description],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            # Step 3 navigation
            self.tasks_step.prev_btn.click(
                fn=lambda step: step - 1,
                inputs=[current_step],
                outputs=[current_step],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            self.tasks_step.next_btn.click(
                fn=lambda step: step + 1,
                inputs=[current_step],
                outputs=[current_step],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            # Connect task_data between steps
            self.tasks_step.generate_btn.click(
                fn=lambda formatted, tasks: tasks,
                inputs=[self.tasks_step.tasks_display, self.tasks_step.task_state],
                outputs=[task_data],
            )

            # Step 4 navigation
            self.github_step.prev_btn.click(
                fn=lambda step: step - 1,
                inputs=[current_step],
                outputs=[current_step],
            ).then(
                fn=update_visibility,
                inputs=[current_step],
                outputs=[step1_group, step2_group, step3_group, step4_group],
            )

            # Pass task data to GitHub step
            current_step.change(
                fn=lambda step, tasks: tasks if step == 4 else gr.skip(),
                inputs=[current_step, task_data],
                outputs=[self.github_step.task_state],
            )

        return workflow_ui
