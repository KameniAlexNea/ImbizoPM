"""
Entry point for launching the ImbizoPM UI application.
"""

import argparse
import os

from dotenv import load_dotenv
from loguru import logger

from imbizopm.ui.launcher import main as main_base
from imbizopm_agents.imbizopm import main as main_agent


def load_environment(env_file_path=None):
    """Loads environment variables from a .env file."""
    if env_file_path:
        if os.path.exists(env_file_path):
            load_dotenv(env_file_path)
            logger.info(f"Loaded configuration from {env_file_path}")
        else:
            logger.warning(f"Environment file {env_file_path} not found")
    else:
        # Default .env file in the current directory
        if load_dotenv():
            logger.info("Loaded configuration from default .env file")
        else:
            logger.info("No default .env file found or loaded.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ImbizoPM UI Application Launcher")
    parser.add_argument(
        "--agent",
        default=True,
        action="store_true",
        help="Launch the ImbizoPM Agent-based Planner UI.",
    )
    parser.add_argument(
        "--share", action="store_true", help="Create a public link for sharing (Gradio)"
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Server address to listen on"
    )
    parser.add_argument(
        "--port", type=int, default=7860, help="Port to run the server on"
    )
    parser.add_argument(
        "--env-file", type=str, help="Path to .env file with configuration"
    )

    args = parser.parse_args()

    # Load environment variables first
    load_environment(args.env_file)

    logger.info(f"Starting ImbizoPM UI on http://{args.host}:{args.port}")
    if args.agent:
        logger.info("Launching Agent-based Planner UI...")
        demo = main_agent(share=args.share, server_name=args.host, server_port=args.port)
    else:
        logger.info("Launching Base UI...")
        # Pass necessary arguments to the base UI launcher
        main_base(share=args.share, host=args.host, port=args.port)
