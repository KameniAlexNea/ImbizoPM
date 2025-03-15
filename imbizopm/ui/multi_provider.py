"""
Multi-provider UI components for ImbizoPM.
"""

import json
from typing import Dict, List, Tuple

import gradio as gr

from ..config import config
from ..project_generator import MultiProviderProjectGenerator
from .base import BaseUI


class MultiProviderUI(BaseUI):
    """UI components for working with multiple LLM providers."""
    
    def __init__(self):
        """Initialize the multi-provider UI components."""
        super().__init__()
    
    def _multi_provider_generate(
        self, 
        project_idea: str,
        use_openai: bool,
        use_anthropic: bool,
        use_ollama: bool,
        master_provider: str
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
                master_provider_idx=master_idx
            )
            
            # Generate description
            return generator.generate_project_description(project_idea)
            
        except Exception as e:
            return f"Error generating project description: {str(e)}"

    def _multi_provider_generate_tasks(
        self, 
        project_description: str,
        use_openai: bool,
        use_anthropic: bool,
        use_ollama: bool,
        master_provider: str
    ) -> Tuple[str, Dict]:
        """
        Generate project tasks using multiple providers.
        """
        if not project_description.strip():
            return "Please enter a project description.", {}
        
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
            return "Please select at least one provider.", {}
        
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
                master_provider_idx=master_idx
            )
            
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
        """Build the UI for multi-provider generation."""
        with gr.Blocks(theme=self.theme) as multi_provider_ui:
            # Multi-provider project description section
            with gr.Row():
                with gr.Column(scale=1):
                    project_idea = gr.Textbox(
                        label="Project Idea", 
                        placeholder="Enter a brief description of your project idea", 
                        lines=3
                    )
                    
                    gr.Markdown("### Providers to Use")
                    with gr.Row():
                        use_openai = gr.Checkbox(
                            label="OpenAI", 
                            value="openai" in self.available_providers, 
                            interactive="openai" in self.available_providers
                        )
                        use_anthropic = gr.Checkbox(
                            label="Anthropic", 
                            value="anthropic" in self.available_providers,
                            interactive="anthropic" in self.available_providers
                        )
                        use_ollama = gr.Checkbox(
                            label="Ollama", 
                            value="ollama" in self.available_providers, 
                            interactive="ollama" in self.available_providers
                        )
                    
                    master_provider = gr.Dropdown(
                        choices=[p for p in self.available_providers if p != "none"],
                        label="Master Provider (for aggregation)",
                        value=self.available_providers[0] if self.available_providers and self.available_providers[0] != "none" else None
                    )
                    
                    generate_btn = gr.Button("Generate with Multiple Providers", variant="primary")
                
                with gr.Column(scale=2):
                    multi_description = gr.Markdown(label="Generated Description")
            
            gr.Markdown("---")
            
            # Multi-provider task generation section
            with gr.Row():
                with gr.Column(scale=1):
                    task_description = gr.Textbox(
                        label="Project Description", 
                        placeholder="Paste your project description here", 
                        lines=6
                    )
                    
                    gr.Markdown("### Providers to Use")
                    with gr.Row():
                        task_use_openai = gr.Checkbox(
                            label="OpenAI", 
                            value="openai" in self.available_providers, 
                            interactive="openai" in self.available_providers
                        )
                        task_use_anthropic = gr.Checkbox(
                            label="Anthropic", 
                            value="anthropic" in self.available_providers,
                            interactive="anthropic" in self.available_providers
                        )
                        task_use_ollama = gr.Checkbox(
                            label="Ollama", 
                            value="ollama" in self.available_providers, 
                            interactive="ollama" in self.available_providers
                        )
                    
                    task_master_provider = gr.Dropdown(
                        choices=[p for p in self.available_providers if p != "none"],
                        label="Master Provider (for aggregation)",
                        value=self.available_providers[0] if self.available_providers and self.available_providers[0] != "none" else None
                    )
                    
                    generate_tasks_btn = gr.Button("Generate Tasks with Multiple Providers", variant="primary")
                    
                    # Export options
                    with gr.Row():
                        export_filename = gr.Textbox(
                            label="Export Filename", 
                            placeholder="tasks.json", 
                            value="tasks.json"
                        )
                        export_btn = gr.Button("Export as JSON", variant="secondary")
                
                with gr.Column(scale=2):
                    multi_tasks_display = gr.Markdown(label="Generated Tasks")

            # Task state for storing generated task data
            task_state = gr.State({})
            
            # Set up event handlers
            generate_btn.click(
                fn=self._multi_provider_generate,
                inputs=[project_idea, use_openai, use_anthropic, use_ollama, master_provider],
                outputs=[multi_description],
                queue=True
            )
            
            generate_tasks_btn.click(
                fn=self._multi_provider_generate_tasks,
                inputs=[task_description, task_use_openai, task_use_anthropic, task_use_ollama, task_master_provider],
                outputs=[multi_tasks_display, task_state],
                queue=True
            )
            
            export_btn.click(
                fn=self._export_tasks_to_json,
                inputs=[task_state, export_filename],
                outputs=[multi_tasks_display]
            )
            
        return multi_provider_ui
