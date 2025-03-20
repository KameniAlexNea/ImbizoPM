"""
Main UI module for ImbizoPM.
"""

import gradio as gr

from ..config import config
from .base import BaseUI
from .workflow_steps.api_key import APIKeyManager
from .workflow_steps.github_step import GitHubStep
from .workflow_ui import WorkflowUI


def launch_ui(
    share: bool = False, server_name: str = "0.0.0.0", server_port: int = 7860
):
    """
    Launch the ImbizoPM Gradio interface.

    Args:
        share: Whether to create a public link for the interface
        server_name: Server address to listen on
        server_port: Port to run the server on
    """
    # Create base UI for theme and configuration
    base_ui = BaseUI()

    # Initialize UI components
    workflow_ui = WorkflowUI()

    # Create the main UI with tabs
    with gr.Blocks(theme=base_ui.theme, title="ImbizoPM - Project Manager") as app:
        gr.Markdown(
            """
            # ImbizoPM Project Manager
            
            Create and manage GitHub projects with AI assistance.
            """
        )

        # Check for available providers and show warning if none
        if (
            len(base_ui.available_providers) == 1
            and base_ui.available_providers[0] == "none"
        ):
            gr.Markdown(
                """
                ⚠️ **Warning**: No LLM providers are configured. Set up API keys in your .env file.
                
                Example configuration:
                ```
                OPENAI_API_KEY=your_openai_api_key
                ANTHROPIC_API_KEY=your_anthropic_api_key
                OLLAMA_BASE_URL=http://localhost:11434
                ```
                
                Until providers are configured, functionality will be limited.
                """
            )

        # Check for GitHub token
        if not config.github_token:
            gr.Markdown(
                """
                ⚠️ **Warning**: GitHub token not found. Set GITHUB_TOKEN in your .env file for GitHub integration.
                """
            )

        with gr.Tabs() as tabs:
            # API Key Tab
            with gr.Tab("API Keys"):
                APIKeyManager().create_interface()

            # Workflow Tab (New)
            with gr.Tab("Project Workflow"):
                workflow_ui.build_ui()

            # GitHub Tab (New)
            with gr.Tab("GitHub Step"):
                GitHubStep().build_step(True)

            # About Tab
            with gr.Tab("About"):
                gr.Markdown(
                    """
                    ## About ImbizoPM
                    
                    ImbizoPM is a tool to help you get started with your GitHub projects by automating the creation of repositories, 
                    projects, and issues. It uses AI to generate comprehensive project descriptions and task lists.
                    
                    ### Features
                    
                    - Generate project descriptions using AI
                    - Create structured task lists with hierarchical organization
                    - Automatically create GitHub repositories, project boards, and issues
                    - Use multiple AI providers together for better results
                    
                    ### Configuration
                    
                    Set your LLM API keys and GitHub token in a .env file or as environment variables.
                    
                    ```
                    # GitHub Authentication
                    GITHUB_TOKEN=your_github_token_here
                    
                    # LLM API Keys
                    OPENAI_API_KEY=your_openai_api_key_here
                    ANTHROPIC_API_KEY=your_anthropic_api_key_here
                    
                    # Ollama Configuration (default is http://localhost:11434)
                    OLLAMA_BASE_URL=http://localhost:11434
                    OLLAMA_MODEL=phi4
                    ```
                    """
                )

    # Launch the app
    app.launch(share=share, server_name=server_name, server_port=server_port)
