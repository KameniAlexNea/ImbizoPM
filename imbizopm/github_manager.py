"""
GitHub Project and Issue Manager.

This module provides functionality to create repositories, projects, and issues on GitHub.
"""

import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from github import Github, GithubException


class GitHubManager:
    """
    A class to manage GitHub repositories, projects, and issues.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub manager.

        Args:
            token: GitHub personal access token. 
            If not provided, will look for 'GITHUB_TOKEN' in environment.
        """
        # Load environment variables
        load_dotenv()

        # Use provided token or get from environment
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GitHub token is required. "
                "Provide it as an argument or set GITHUB_TOKEN environment variable."
            )

        # Initialize GitHub client
        self.github = Github(self.token)
        self.user = self.github.get_user()

    def create_repository(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = False,
        has_issues: bool = True,
        has_wiki: bool = True,
        auto_init: bool = True,
    ) -> Dict:
        """
        Create a new GitHub repository.

        Args:
            name: Repository name
            description: Repository description
            private: Whether the repository should be private
            has_issues: Whether the repository should have issues enabled
            has_wiki: Whether the repository should have wiki enabled
            auto_init: Whether to auto-initialize with README

        Returns:
            Dictionary with repository details
        """
        try:
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private,
                has_issues=has_issues,
                has_wiki=has_wiki,
                auto_init=auto_init,
            )
            return {
                "success": True,
                "repository": {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "url": repo.html_url,
                    "clone_url": repo.clone_url,
                },
            }
        except GithubException as e:
            return {"success": False, "error": f"Failed to create repository: {str(e)}"}

    def create_project(
        self, repo_name: str, project_name: str, body: Optional[str] = None
    ) -> Dict:
        """
        Create a new project board in a repository.

        Args:
            repo_name: Repository name
            project_name: Project name
            body: Project description

        Returns:
            Dictionary with project details
        """
        try:
            repo = self.github.get_repo(f"{self.user.login}/{repo_name}")
            project = repo.create_project(name=project_name, body=body)

            # Create default columns (To Do, In Progress, Done)
            project.create_column("To Do")
            project.create_column("In Progress")
            project.create_column("Done")

            return {
                "success": True,
                "project": {
                    "name": project.name,
                    "url": project.html_url,
                    "columns": ["To Do", "In Progress", "Done"],
                },
            }
        except GithubException as e:
            return {"success": False, "error": f"Failed to create project: {str(e)}"}

    def create_issue(
        self,
        repo_name: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        milestone: Optional[int] = None,
        assignees: Optional[List[str]] = None,
    ) -> Dict:
        """
        Create a new issue in a repository.

        Args:
            repo_name: Repository name
            title: Issue title
            body: Issue description
            labels: List of labels to apply
            milestone: Milestone ID
            assignees: List of usernames to assign

        Returns:
            Dictionary with issue details
        """
        try:
            repo = self.github.get_repo(f"{self.user.login}/{repo_name}")
            issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels,
                milestone=milestone,
                assignees=assignees,
            )

            return {
                "success": True,
                "issue": {
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url,
                },
            }
        except GithubException as e:
            return {"success": False, "error": f"Failed to create issue: {str(e)}"}

    def create_project_with_issues(
        self,
        repo_name: str,
        project_name: str,
        project_description: Optional[str] = None,
        issues: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Create a project and populate it with issues.

        Args:
            repo_name: Repository name
            project_name: Project name
            project_description: Project description
            issues: List of dictionaries with issue details (title, body, labels)

        Returns:
            Dictionary with project and issues details
        """
        # Create project
        project_result = self.create_project(
            repo_name, project_name, project_description
        )
        if not project_result["success"]:
            return project_result

        # Create issues if provided
        created_issues = []
        if issues:
            for issue_data in issues:
                issue_result = self.create_issue(
                    repo_name=repo_name,
                    title=issue_data.get("title"),
                    body=issue_data.get("body"),
                    labels=issue_data.get("labels"),
                    assignees=issue_data.get("assignees"),
                )
                if issue_result["success"]:
                    created_issues.append(issue_result["issue"])
                else:
                    created_issues.append({"error": issue_result["error"]})

        return {
            "success": True,
            "project": project_result["project"],
            "issues": created_issues,
        }
