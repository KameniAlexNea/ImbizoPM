"""
Script to launch the ImbizoPM UI.
"""

from loguru import logger

from .main import launch_ui


def main(share: bool = False, host: str = "0.0.0.0", port: int = 7860):
    """Launches the base ImbizoPM UI with provided settings."""
    # Environment loading is now handled by the main app.py entry point

    # Launch the UI using the passed arguments
    logger.info(f"Launching Base UI via launch_ui function...")
    launch_ui(share=share, server_name=host, server_port=port)
