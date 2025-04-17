"""
Entry point for launching the ImbizoPM UI application.
"""

from argparse import ArgumentParser

from imbizopm.ui.launcher import main as main_base
from imbizopm_agents.imbizopm import main as main_agent

args = ArgumentParser(description="ImbizoPM UI Application")
args.add_argument(
    "--agent",
    action="store_true",
    help="Launch the ImbizoPM UI application with the agent.",
)
args = args.parse_args()
if args.agent:
    main_agent()
else:
    main_base()
