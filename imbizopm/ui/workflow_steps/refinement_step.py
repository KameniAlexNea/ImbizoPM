"""
Project refinement step for the workflow UI.
"""

import gradio as gr

from ...config import config
from ...project_generator import ProjectGenerator
from .base_step import BaseWorkflowStep


class RefinementStep(BaseWorkflowStep):
    """Project description refinement step."""
    
    def __init__(self):
        """Initialize the refinement step."""
        super().__init__()
        # UI elements will be set during build_step
        self.current_description = None
        self.feedback = None
        self.refine_btn = None
        self.refined_description = None
        self.prev_btn = None
        self.skip_btn = None
        self.next_btn = None
        
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

            # Refine description with streaming
            return generator.refine_project_description(original_description, feedback)

        except Exception as e:
            return f"Error refining project description: {str(e)}"
            
    def build_step(self, visible: bool = False) -> None:
        """Build the UI for the refinement step."""
        gr.Markdown("## Step 2: Project Review & Refinement")
        
        with gr.Row():
            with gr.Column(scale=1):
                self.current_description = gr.Markdown(label="Current Description")
                self.feedback = gr.Textbox(
                    label="Feedback for Improvement",
                    placeholder="What would you like to improve or add to the description?",
                    lines=3,
                )
                
                # Use the first available provider
                self.provider = gr.Dropdown(
                    choices=self.available_providers,
                    label="LLM Provider",
                    value=(
                        self.available_providers[0]
                        if self.available_providers
                        else "none"
                    ),
                    visible=True,
                )
                self.model = gr.Textbox(
                    label="Model (optional)",
                    placeholder="Leave blank for default model",
                    visible=True,
                )
                
                self.refine_btn = gr.Button("Refine Description", variant="primary")
                
            with gr.Column(scale=1):
                self.refined_description = gr.Markdown(
                    label="Refined Description",
                    value="Refined description will appear here...",
                )
        
        # Navigation buttons
        with gr.Row():
            self.prev_btn = gr.Button("Back", variant="secondary")
            self.skip_btn = gr.Button("Skip Refinement", variant="secondary")
            self.next_btn = gr.Button("Accept & Generate Tasks", variant="primary")
            
        # Register event handlers
        self.register_event_handlers()
    
    def register_event_handlers(self) -> None:
        """Register event handlers for this step's UI elements."""

        def update_step(text1: str, text2: str):
            if text2 and text2 != "Refined description will appear here...":
                return text2
            return text1
        # Refine description
        self.refine_btn.click(
            fn=update_step,
            inputs=[self.current_description, self.refined_description],
            outputs=[self.current_description],
            queue=True,
        ).success(
            fn=self._refine_project_description,
            inputs=[self.current_description, self.feedback, self.provider, self.model],
            outputs=[self.refined_description],
            queue=True,
        )
