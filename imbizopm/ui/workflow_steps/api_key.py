import gradio as gr

from ...config import APIKeys


class APIKeyManager:
    """
    A class for managing API keys for various AI services.
    Keys are stored in memory during runtime.
    """

    def __init__(self):
        """Initialize the API key manager with empty keys."""
        # Initialize textbox attributes to None
        self.openai_key_textbox = None
        self.anthropic_key_textbox = None
        self.ollama_url_textbox = None
        self.github_token = None

        # Initialize interface attribute
        self.interface = None

    def save_all_api_keys(self, openai_key, anthropic_key, ollama_url, github_token):
        """Save all API keys at once in memory."""
        APIKeys.openai_key = openai_key
        APIKeys.openai_key = anthropic_key
        APIKeys.ollama_url = ollama_url or "http://localhost:11434"
        APIKeys.github_token = github_token

        return "All API keys saved successfully!"

    def create_interface(self):
        """Create the Gradio interface for API key management."""
        with gr.Blocks(title="API Key Management") as interface:
            gr.Markdown("# API Key Management")
            gr.Markdown("Enter your API keys for various AI services below.")

            with gr.Tab("OpenAI"):
                self.openai_key_textbox = gr.Textbox(
                    label="OpenAI API Key",
                    placeholder="sk-...",
                    type="password",
                    value=APIKeys.openai_key,
                )

            with gr.Tab("Anthropic"):
                self.anthropic_key_textbox = gr.Textbox(
                    label="Anthropic API Key",
                    placeholder="sk-ant-...",
                    type="password",
                    value=APIKeys.anthropic_key,
                )

            with gr.Tab("Ollama"):
                self.ollama_url_textbox = gr.Textbox(
                    label="Ollama Server URL",
                    placeholder="http://localhost:11434",
                    value=APIKeys.ollama_url,
                )

            with gr.Tab("Github"):
                self.github_token = gr.Textbox(
                    label="Github Token",
                    placeholder="gh...",
                    type="password",
                    value=APIKeys.github_token,
                )

            # Single save button for all keys
            save_all = gr.Button("Save All Keys", variant="primary")
            status_output = gr.Textbox(label="Status")

            save_all.click(
                fn=self.save_all_api_keys,
                inputs=[
                    self.openai_key_textbox,
                    self.anthropic_key_textbox,
                    self.ollama_url_textbox,
                    self.github_token,
                ],
                outputs=status_output,
            )

        # Store the interface as an attribute
        self.interface = interface
        return interface


def create_api_key_interface():
    """Legacy function for backward compatibility."""
    manager = APIKeyManager()
    return manager.create_interface()


if __name__ == "__main__":
    # When run directly, launch the interface
    manager = APIKeyManager()
    app = manager.create_interface()
    app.launch()
