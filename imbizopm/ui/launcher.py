"""
Script to launch the ImbizoPM UI.
"""

import argparse
import os

from dotenv import load_dotenv

from .main import launch_ui


def main():
    """CLI entry point for the UI launcher."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Launch the ImbizoPM UI")
    parser.add_argument(
        "--share", action="store_true", help="Create a public link for sharing"
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

    # Load environment variables if env-file is specified
    if args.env_file:
        if os.path.exists(args.env_file):
            load_dotenv(args.env_file)
            print(f"Loaded configuration from {args.env_file}")
        else:
            print(f"Warning: Environment file {args.env_file} not found")
    else:
        # Default .env file in the current directory
        load_dotenv()

    # Launch the UI
    print(f"Starting ImbizoPM UI on http://{args.host}:{args.port}")
    launch_ui(share=args.share, server_name=args.host, server_port=args.port)


if __name__ == "__main__":
    main()
