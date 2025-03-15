"""
Tests for the GitHub manager module.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from github import GithubException

from imbizopm.github_manager import GitHubManager


class TestGitHubManager(unittest.TestCase):
    """Test cases for the GitHub manager."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the GitHub API
        self.mock_github = MagicMock()
        self.mock_user = MagicMock()
        self.mock_repo = MagicMock()

        # Configure mocks
        self.mock_github.get_user.return_value = self.mock_user
        self.mock_user.login = "test-user"
        self.mock_user.get_repo.return_value = self.mock_repo
        self.mock_github.get_repo.return_value = self.mock_repo

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    @patch("imbizopm.github_manager.Github")
    def test_init_with_env_token(self, mock_github_class):
        """Test initializing with token from environment."""
        mock_github_class.return_value = self.mock_github

        manager = GitHubManager()

        mock_github_class.assert_called_once_with("test_token")
        self.assertEqual(manager.token, "test_token")

    @patch("imbizopm.github_manager.Github")
    def test_init_with_provided_token(self, mock_github_class):
        """Test initializing with provided token."""
        mock_github_class.return_value = self.mock_github

        manager = GitHubManager(token="provided_token")

        mock_github_class.assert_called_once_with("provided_token")
        self.assertEqual(manager.token, "provided_token")

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_token(self):
        """Test initializing without a token raises an error."""
        with self.assertRaises(ValueError):
            GitHubManager()

    @patch("imbizopm.github_manager.Github")
    def test_create_repository_success(self, mock_github_class):
        """Test successful repository creation."""
        # Setup
        mock_github_class.return_value = self.mock_github
        mock_repo = MagicMock()
        mock_repo.name = "test-repo"
        mock_repo.full_name = "test-user/test-repo"
        mock_repo.html_url = "https://github.com/test-user/test-repo"
        mock_repo.clone_url = "https://github.com/test-user/test-repo.git"
        self.mock_user.create_repo.return_value = mock_repo

        # Execute
        manager = GitHubManager(token="test_token")
        result = manager.create_repository(
            name="test-repo", description="Test repo description", private=True
        )

        # Assert
        self.mock_user.create_repo.assert_called_once_with(
            name="test-repo",
            description="Test repo description",
            private=True,
            has_issues=True,
            has_wiki=True,
            auto_init=True,
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["repository"]["name"], "test-repo")
        self.assertEqual(result["repository"]["full_name"], "test-user/test-repo")

    @patch("imbizopm.github_manager.Github")
    def test_create_repository_failure(self, mock_github_class):
        """Test repository creation failure."""
        # Setup
        mock_github_class.return_value = self.mock_github
        self.mock_user.create_repo.side_effect = GithubException(
            status=422, data={"message": "Repository already exists"}
        )

        # Execute
        manager = GitHubManager(token="test_token")
        result = manager.create_repository(name="test-repo")

        # Assert
        self.assertFalse(result["success"])
        self.assertIn("Failed to create repository", result["error"])

    @patch("imbizopm.github_manager.Github")
    def test_create_project_success(self, mock_github_class):
        """Test successful project creation."""
        # Setup
        mock_github_class.return_value = self.mock_github
        mock_project = MagicMock()
        mock_project.name = "Test Project"
        mock_project.html_url = "https://github.com/test-user/test-repo/projects/1"
        self.mock_repo.create_project.return_value = mock_project

        # Execute
        manager = GitHubManager(token="test_token")
        result = manager.create_project(
            repo_name="test-repo",
            project_name="Test Project",
            body="Test project description",
        )

        # Assert
        self.mock_github.get_repo.assert_called_once_with("test-user/test-repo")
        self.mock_repo.create_project.assert_called_once_with(
            name="Test Project", body="Test project description"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["project"]["name"], "Test Project")
        self.assertEqual(result["project"]["columns"], ["To Do", "In Progress", "Done"])

    @patch("imbizopm.github_manager.Github")
    def test_create_issue_success(self, mock_github_class):
        """Test successful issue creation."""
        # Setup
        mock_github_class.return_value = self.mock_github
        mock_issue = MagicMock()
        mock_issue.number = 1
        mock_issue.title = "Test Issue"
        mock_issue.html_url = "https://github.com/test-user/test-repo/issues/1"
        self.mock_repo.create_issue.return_value = mock_issue

        # Execute
        manager = GitHubManager(token="test_token")
        result = manager.create_issue(
            repo_name="test-repo",
            title="Test Issue",
            body="Test issue description",
            labels=["bug", "help wanted"],
            assignees=["contributor"],
        )

        # Assert
        self.mock_github.get_repo.assert_called_once_with("test-user/test-repo")
        self.mock_repo.create_issue.assert_called_once_with(
            title="Test Issue",
            body="Test issue description",
            labels=["bug", "help wanted"],
            milestone=None,
            assignees=["contributor"],
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["issue"]["number"], 1)
        self.assertEqual(result["issue"]["title"], "Test Issue")

    @patch("imbizopm.github_manager.Github")
    def test_create_project_with_issues_success(self, mock_github_class):
        """Test successful creation of project with issues."""
        # Setup
        mock_github_class.return_value = self.mock_github

        # Mock project
        mock_project = MagicMock()
        mock_project.name = "Test Project"
        mock_project.html_url = "https://github.com/test-user/test-repo/projects/1"
        self.mock_repo.create_project.return_value = mock_project

        # Mock issues
        mock_issue1 = MagicMock()
        mock_issue1.number = 1
        mock_issue1.title = "Issue 1"
        mock_issue1.html_url = "https://github.com/test-user/test-repo/issues/1"

        mock_issue2 = MagicMock()
        mock_issue2.number = 2
        mock_issue2.title = "Issue 2"
        mock_issue2.html_url = "https://github.com/test-user/test-repo/issues/2"

        self.mock_repo.create_issue.side_effect = [mock_issue1, mock_issue2]

        # Test data
        issue_data = [
            {"title": "Issue 1", "body": "Description 1", "labels": ["enhancement"]},
            {"title": "Issue 2", "body": "Description 2", "labels": ["bug"]},
        ]

        # Execute
        manager = GitHubManager(token="test_token")
        result = manager.create_project_with_issues(
            repo_name="test-repo",
            project_name="Test Project",
            project_description="Test project description",
            issues=issue_data,
        )

        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["project"]["name"], "Test Project")
        self.assertEqual(len(result["issues"]), 2)
        self.assertEqual(result["issues"][0]["title"], "Issue 1")
        self.assertEqual(result["issues"][1]["title"], "Issue 2")

    @patch("imbizopm.github_manager.Github")
    def test_list_issues(self, mock_github_class):
        """Test listing issues from a repository."""
        # Setup
        mock_github_class.return_value = self.mock_github

        # Mock issues
        mock_issue1 = MagicMock()
        mock_issue1.number = 1
        mock_issue1.title = "Issue 1"
        mock_issue1.state = "open"
        mock_issue1.html_url = "https://github.com/test-user/test-repo/issues/1"

        mock_issue2 = MagicMock()
        mock_issue2.number = 2
        mock_issue2.title = "Issue 2"
        mock_issue2.state = "closed"
        mock_issue2.html_url = "https://github.com/test-user/test-repo/issues/2"

        self.mock_repo.get_issues.return_value = [mock_issue1, mock_issue2]

        # Execute
        manager = GitHubManager(token="test_token")
        result = manager.list_issues(repo_name="test-repo")

        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["repository"], "test-repo")
        self.assertEqual(result["issues_count"], 2)
        self.assertEqual(result["issues"][0]["number"], 1)
        self.assertEqual(result["issues"][0]["state"], "open")
        self.assertEqual(result["issues"][1]["number"], 2)
        self.assertEqual(result["issues"][1]["state"], "closed")


if __name__ == "__main__":
    unittest.main()
