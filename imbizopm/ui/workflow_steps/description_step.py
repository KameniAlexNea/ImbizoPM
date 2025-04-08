"""
Project description generation step for the workflow UI.
"""

from typing import Tuple

import gradio as gr

from ...config import config
from ...project_generator import (
    MultiProviderProjectGenerator,
    ProjectGenerator,
)
from .base_step import BaseWorkflowStep


class DescriptionStep(BaseWorkflowStep):
    """Project description generation step."""

    def __init__(self):
        """Initialize the description step."""
        super().__init__()
        # UI elements will be set during build_step
        self.project_idea = None
        self.use_single_provider = None
        self.provider = None
        self.model = None
        self.multi_provider_options = None
        self.use_openai = None
        self.use_anthropic = None
        self.use_ollama = None
        self.master_provider = None
        self.generate_btn = None
        self.project_description = None
        self.next_btn = None

    def _generate_project_description(
        self, project_idea: str, provider: str, model: str = None
    ):
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

            text = ""
            for t in generator.generate_project_description(project_idea):
                text += t
                yield text
        except Exception as e:
            yield f"Error generating project description: {str(e)}"

    def _multi_provider_generate(
        self,
        project_idea: str,
        use_openai: bool,
        use_anthropic: bool,
        use_ollama: bool,
        master_provider: str,
    ):
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

            # Generate description with streaming
            text = ""
            for t in generator.generate_project_description(project_idea):
                text += t
                yield text

        except Exception as e:
            yield f"Error generating project description: {str(e)}"

    def generate_description(
        self,
        idea: str,
        use_single: bool,
        prov: str,
        mod: str,
        use_oa: bool,
        use_an: bool,
        use_ol: bool,
        master_prov: str,
    ):
        """Generate project description using either single or multiple providers."""
        if use_single:
            yield from self._generate_project_description(idea, prov, mod)
        else:
            yield from self._multi_provider_generate(
                idea, use_oa, use_an, use_ol, master_prov
            )

    def enable_next_button(self, description: str) -> gr.Button:
        """Enable or disable the next button based on description content."""
        # Check if description is not empty and not an error message
        valid = (
            description
            and description != "Project description will appear here..."
            and not description.startswith("Error")
            and not description.startswith("Please select")
        )
        return gr.Button(interactive=valid)

    def toggle_provider_options(self, use_single: bool) -> Tuple[gr.Group, gr.Group]:
        """Toggle visibility of single vs. multi-provider options."""
        return (
            gr.Group(visible=use_single),  # Single provider options
            gr.Group(visible=not use_single),  # Multi-provider options
        )

    def build_step(self, visible: bool = False) -> None:
        """Build the UI for the description step."""
        gr.Markdown("## Step 1: Project Idea")

        with gr.Row():
            with gr.Column(scale=1):
                self.project_idea = gr.Textbox(
                    label="Project Idea",
                    placeholder="Enter a brief description of your project idea",
                    lines=5,
                )

                with gr.Accordion("Configuration", open=False):
                    # Single provider options
                    with gr.Group() as single_provider_group:
                        self.use_single_provider = gr.Checkbox(
                            label="Use Single Provider", value=True
                        )
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

                        # Get default model name for the selected provider
                        default_model = None
                        if (
                            self.available_providers
                            and self.available_providers[0] != "none"
                        ):
                            try:
                                default_model = config.models.get_provider_config(
                                    self.available_providers[0]
                                ).default_model.name
                            except (ValueError, AttributeError):
                                default_model = ""

                        # Use a textbox for model input instead of dropdown
                        self.model = gr.Textbox(
                            label="Model",
                            placeholder="Enter model or deployment name",
                            value=default_model if default_model else "",
                            visible=True,
                        )

                    # Multi-provider options
                    with gr.Group(visible=False) as self.multi_provider_options:
                        gr.Markdown("#### Providers to Use")
                        with gr.Row():
                            self.use_openai = gr.Checkbox(
                                label="OpenAI",
                                value="openai" in self.available_providers,
                                interactive="openai" in self.available_providers,
                            )
                            self.use_anthropic = gr.Checkbox(
                                label="Anthropic",
                                value="anthropic" in self.available_providers,
                                interactive="anthropic" in self.available_providers,
                            )
                            self.use_ollama = gr.Checkbox(
                                label="Ollama",
                                value="ollama" in self.available_providers,
                                interactive="ollama" in self.available_providers,
                            )

                        self.master_provider = gr.Dropdown(
                            choices=[
                                p for p in self.available_providers if p != "none"
                            ],
                            label="Master Provider (for aggregation)",
                            value=(
                                config.master_provider
                                if config.master_provider in self.available_providers
                                else (
                                    self.available_providers[0]
                                    if self.available_providers
                                    and self.available_providers[0] != "none"
                                    else None
                                )
                            ),
                        )

                self.generate_btn = gr.Button(
                    "Generate Project Description", variant="primary"
                )

            with gr.Column(scale=1):
                self.project_description = gr.Markdown(
                    label="Generated Description",
                    value="Project description will appear here...",
                    show_copy_button=True,
                )

        # Navigation buttons
        with gr.Row():
            self.next_btn = gr.Button(
                "Next: Review & Refine", variant="secondary", interactive=False
            )

        # Register event handlers
        self.register_event_handlers(single_provider_group)

    def update_model_default(self, provider: str) -> gr.Textbox:
        """Update the model input field with the default model for the selected provider."""
        if provider == "none" or not provider:
            return gr.Textbox(value="")

        try:
            default_model = config.models.get_provider_config(
                provider
            ).default_model.name
            return gr.Textbox(value=default_model)
        except (ValueError, AttributeError):
            return gr.Textbox(value="")

    def register_event_handlers(self, single_provider_group) -> None:
        """Register event handlers for this step's UI elements."""
        # Toggle between single and multi provider options
        self.use_single_provider.change(
            fn=self.toggle_provider_options,
            inputs=[self.use_single_provider],
            outputs=[single_provider_group, self.multi_provider_options],
        )

        # Update the model textbox with appropriate default when provider changes
        self.provider.change(
            fn=self.update_model_default,
            inputs=[self.provider],
            outputs=[self.model],
        )

        # Generate description
        self.generate_btn.click(
            fn=self.generate_description,
            inputs=[
                self.project_idea,
                self.use_single_provider,
                self.provider,
                self.model,
                self.use_openai,
                self.use_anthropic,
                self.use_ollama,
                self.master_provider,
            ],
            outputs=[self.project_description],
            queue=True,
        ).then(
            fn=self.enable_next_button,
            inputs=[self.project_description],
            outputs=[self.next_btn],
        )
