"""
Command-line interface for ImbizoPM.
"""

import argparse
import json
import sys
from typing import Any, Dict, List

from .github_manager import GitHubManager


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="ImbizoPM - GitHub Project Manager")

    # Main subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Repository creation command
    repo_parser = subparsers.add_parser(
        "create-repo", help="Create a GitHub repository"
    )
    repo_parser.add_argument("--name", required=True, help="Repository name")
    repo_parser.add_argument("--description", help="Repository description")
    repo_parser.add_argument(
        "--private", action="store_true", help="Make repository private"
    )

    # Project creation command
    project_parser = subparsers.add_parser(
        "create-project", help="Create a GitHub project"
    )
    project_parser.add_argument("--repo", required=True, help="Repository name")
    project_parser.add_argument("--name", required=True, help="Project name")
    project_parser.add_argument("--description", help="Project description")

    # Issue creation command
    issue_parser = subparsers.add_parser("create-issue", help="Create a GitHub issue")
    issue_parser.add_argument("--repo", required=True, help="Repository name")
    issue_parser.add_argument("--title", required=True, help="Issue title")
    issue_parser.add_argument("--body", help="Issue body text")
    issue_parser.add_argument("--labels", nargs="+", help="Labels to apply")
    issue_parser.add_argument("--assignees", nargs="+", help="Users to assign")

    # Project with issues command
    full_parser = subparsers.add_parser(
        "create-full-project", help="Create a GitHub project with issues"
    )
    full_parser.add_argument("--repo", required=True, help="Repository name")
    full_parser.add_argument("--project-name", required=True, help="Project name")
    full_parser.add_argument("--project-description", help="Project description")
    full_parser.add_argument("--issues-file", help="JSON file with issues definition")

    # Token option for all commands
    parser.add_argument("--token", help="GitHub personal access token")

    return parser.parse_args()


def load_issues_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Load issues definition from a JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading issues file: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    args = parse_args()

    if not args.command:
        print("Please specify a command. Use --help for available commands.")
        sys.exit(1)

    try:
        manager = GitHubManager(token=args.token)

        if args.command == "create-repo":
            result = manager.create_repository(
                name=args.name, description=args.description, private=args.private
            )

        elif args.command == "create-project":
            result = manager.create_project(
                repo_name=args.repo, project_name=args.name, body=args.description
            )

        elif args.command == "create-issue":
            result = manager.create_issue(
                repo_name=args.repo,
                title=args.title,
                body=args.body,
                labels=args.labels,
                assignees=args.assignees,
            )

        elif args.command == "create-full-project":
            issues = None
            if args.issues_file:
                issues = load_issues_from_file(args.issues_file)

            result = manager.create_project_with_issues(
                repo_name=args.repo,
                project_name=args.project_name,
                project_description=args.project_description,
                issues=issues,
            )

        # Print result
        print(json.dumps(result, indent=2))

        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
