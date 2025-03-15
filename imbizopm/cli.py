"""
Command-line interface for ImbizoPM.
"""

import argparse
import json
import sys
from typing import Any, Dict, List

from .config import config
from .github_manager import GitHubManager
from .project_generator import ProjectGenerator


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

    # AI-powered project creation command - NEW
    ai_project_parser = subparsers.add_parser(
        "ai-project", help="Generate project structure using AI and create it on GitHub"
    )
    ai_project_parser.add_argument("--prompt", help="Project idea prompt")
    ai_project_parser.add_argument(
        "--repo",
        help="Repository name (if not provided, will be extracted from generated title)",
    )
    ai_project_parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "anthropic", "ollama"],
        help="LLM provider to use",
    )
    ai_project_parser.add_argument(
        "--model", help="Model name for the selected provider"
    )
    ai_project_parser.add_argument(
        "--private", action="store_true", help="Make repository private"
    )
    ai_project_parser.add_argument(
        "--save-tasks", help="Save generated tasks to a JSON file"
    )
    ai_project_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate tasks without creating GitHub project",
    )

    # Token option for all commands
    parser.add_argument("--token", help="GitHub personal access token")
    parser.add_argument("--api-key", help="API key for LLM provider")

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
        # Handle AI project generation
        if args.command == "ai-project":
            # Initialize the LLM provider
            provider_kwargs = {}

            if args.api_key:
                provider_kwargs["api_key"] = args.api_key
            else:
                # Get configuration from the config module
                provider_kwargs = config.get_llm_config(args.provider)

            if args.model:
                provider_kwargs["model"] = args.model

            try:
                # Initialize the project generator
                generator = ProjectGenerator(args.provider, **provider_kwargs)

                # Get project prompt
                prompt = args.prompt
                if not prompt:
                    prompt = input("Enter your project idea: ")

                # Generate project interactively
                project_data, issues = generator.interactive_project_creation(prompt)

                # Save tasks to file if requested
                if args.save_tasks and project_data:
                    with open(args.save_tasks, "w") as f:
                        json.dump(project_data, f, indent=2)
                    print(f"Tasks saved to {args.save_tasks}")

                # Exit if dry run
                if args.dry_run or not issues:
                    sys.exit(0)

                # Create GitHub resources
                github_token = args.token or config.github_token
                manager = GitHubManager(token=github_token)

                # Determine repository name
                repo_name = args.repo
                if not repo_name:
                    # Generate repo name from project title
                    repo_name = project_data["project_title"].lower().replace(" ", "-")
                    repo_name = "".join(
                        c if c.isalnum() or c == "-" else "" for c in repo_name
                    )
                    print(f"Using repository name: {repo_name}")

                # Create repository
                repo_result = manager.create_repository(
                    name=repo_name,
                    description=project_data.get("project_description", ""),
                    private=args.private,
                )

                if not repo_result["success"]:
                    print(
                        f"Failed to create repository: {repo_result.get('error', 'Unknown error')}"
                    )
                    sys.exit(1)

                # Create project
                project_result = manager.create_project(
                    repo_name=repo_name,
                    project_name=project_data["project_title"],
                    body=project_data.get("project_description", ""),
                )

                if not project_result["success"]:
                    print(
                        f"Failed to create project: {project_result.get('error', 'Unknown error')}"
                    )
                    sys.exit(1)

                # Create issues
                created_issues = []
                for issue in issues:
                    issue_result = manager.create_issue(
                        repo_name=repo_name,
                        title=issue["title"],
                        body=issue["body"],
                        labels=issue.get("labels", []),
                    )
                    if issue_result["success"]:
                        created_issues.append(issue_result["issue"])

                print(
                    f"\nSuccessfully created repository, project, and {len(created_issues)} issues!"
                )
                print(f"Repository URL: {repo_result['repository']['url']}")

                sys.exit(0)

            except Exception as e:
                print(f"Error during AI project generation: {str(e)}")
                sys.exit(1)

        # Handle other commands (existing functionality)
        manager = GitHubManager(token=args.token or config.github_token)

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
