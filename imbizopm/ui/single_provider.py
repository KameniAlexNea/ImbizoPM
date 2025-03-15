"""
Single provider UI components for ImbizoPM.
"""

import json
from typing import Dict, Tuple

import gradio as gr

from ..config import config
from ..project_generator import ProjectGenerator
from .base import BaseUI


class SingleProviderUI(BaseUI):
    """UI components for working with a single LLM provider."""
    
    def __init__(self):
        """Initialize the single provider UI components."""
        super().__init__()
    
    def _generate_project_description(
        self, 
        project_idea: str, 
        provider: str, 
        model: str = None
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

    def _refine_project_description(
        self, 
        original_description: str, 
        feedback: str, 
        provider: str, 
        model: str = None
    ) -> str:
        """
        Refine a project description based on feedback.
        """
        if provider == "none" or not original_description.strip() or not feedback.strip():
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
        self, 
        project_description: str, 
        provider: str, 
        model: str = None
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
            if not filename.lower().endswith('.json'):
                filename += '.json'
            
            with open(filename, 'w') as f:
                json.dump(tasks_data, f, indent=2)
            
            return f"Tasks successfully exported to {filename}"
            
        except Exception as e:
            return f"Error exporting tasks: {str(e)}"
    
    def build_ui(self) -> gr.Blocks:
        """Build the UI for single provider generation."""
        with gr.Blocks(theme=self.theme) as single_provider_ui:
            # Project Description Tab
            with gr.Row():
                with gr.Column(scale=1):
                    provider = gr.Dropdown(
                        choices=self.available_providers,
                        label="LLM Provider",
                        value=self.available_providers[0] if self.available_providers else "none"
                    )
                    model = gr.Textbox(label="Model (optional, leave blank for default)")
                    project_idea = gr.Textbox(
                        label="Project Idea", 
                        placeholder="Enter a brief description of your project idea", 
                        lines=3
                    )
                    generate_btn = gr.Button("Generate Description", variant="primary")
                
                with gr.Column(scale=2):
                    project_description = gr.Markdown(label="Generated Description")
            
            # Feedback and refinement section
            with gr.Row(visible=False) as refinement_row:
                with gr.Column(scale=1):
                    feedback = gr.Textbox(
                        label="Feedback for Improvement",
                        placeholder="What would you like to improve or add to the description?",
                        lines=3
                    )
                    refine_btn = gr.Button("Refine Description", variant="secondary")
                
                with gr.Column(scale=2):
                    refined_description = gr.Markdown(label="Refined Description")
            
            gr.Markdown("---")
            
            # Task Generation Section
            with gr.Row():
                with gr.Column(scale=1):
                    task_provider = gr.Dropdown(
                        choices=self.available_providers,
                        label="LLM Provider",
                        value=self.available_providers[0] if self.available_providers else "none"
                    )
                    task_model = gr.Textbox(label="Model (optional, leave blank for default)")
                    task_description = gr.Textbox(
                        label="Project Description", 
                        placeholder="Paste your project description here", 
                        lines=6
                    )
                    generate_tasks_btn = gr.Button("Generate Tasks", variant="primary")
                    
                    # Export options
                    with gr.Row():
                        export_filename = gr.Textbox(
                            label="Export Filename", 
                            placeholder="tasks.json", 
                            value="tasks.json"
                        )
                        export_btn = gr.Button("Export as JSON", variant="secondary")
                
                with gr.Column(scale=2):
                    tasks_display = gr.Markdown(label="Generated Tasks")

            # Logic for showing refinement section
            def show_refinement_section(description):
                return gr.Row(visible=True) if description and description != "Please select a provider and enter a project idea." else gr.Row(visible=False)

            # Task state for storing generated task data
            task_state = gr.State({})
            
            # Set up event handlers
            generate_btn.click(
                fn=self._generate_project_description,
                inputs=[project_idea, provider, model],
                outputs=[project_description],
                queue=True
            ).then(
                fn=show_refinement_section,
                inputs=[project_description],
                outputs=[refinement_row]
            )
            
            refine_btn.click(
                fn=self._refine_project_description,
                inputs=[project_description, feedback, provider, model],
                outputs=[refined_description],
                queue=True
            )
            
            generate_tasks_btn.click(
                fn=self._generate_project_tasks,
                inputs=[task_description, task_provider, task_model],
                outputs=[tasks_display, task_state],
                queue=True
            )
            
            export_btn.click(
                fn=self._export_tasks_to_json,
                inputs=[task_state, export_filename],
                outputs=[tasks_display]
            )
            
        return single_provider_ui
