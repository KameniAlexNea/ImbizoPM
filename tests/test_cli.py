"""
Tests for the command-line interface module.
"""

import json
import os
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

from imbizopm.cli import main, parse_args


class TestCLI(unittest.TestCase):
    """Test cases for the command-line interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.github_manager_patch = patch("imbizopm.cli.GitHubManager")
        self.mock_github_manager_class = self.github_manager_patch.start()
        self.mock_github_manager = MagicMock()
        self.mock_github_manager_class.return_value = self.mock_github_manager
        
        self.project_generator_patch = patch("imbizopm.cli.ProjectGenerator")
        self.mock_project_generator_class = self.project_generator_patch.start()
        self.mock_project_generator = MagicMock()
        self.mock_project_generator_class.return_value = self.mock_project_generator
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.github_manager_patch.stop()
        self.project_generator_patch.stop()
        
    def test_parse_args_create_repo(self):
        """Test parsing create-repo command arguments."""
        test_args = ["create-repo", "--name", "test-repo", "--description", "Test repository", "--private"]
        
        with patch.object(sys, "argv", ["imbizopm"] + test_args):
            args = parse_args()
            
        self.assertEqual(args.command, "create-repo")
        self.assertEqual(args.name, "test-repo")
        self.assertEqual(args.description, "Test repository")
        self.assertTrue(args.private)
        
    def test_parse_args_create_project(self):
        """Test parsing create-project command arguments."""
        test_args = ["create-project", "--repo", "test-repo", "--name", "Test Project", "--description", "Test project"]
        
        with patch.object(sys, "argv", ["imbizopm"] + test_args):
            args = parse_args()
            
        self.assertEqual(args.command, "create-project")
        self.assertEqual(args.repo, "test-repo")
        self.assertEqual(args.name, "Test Project")
        self.assertEqual(args.description, "Test project")
        
    def test_parse_args_create_issue(self):
        """Test parsing create-issue command arguments."""
        test_args = [
            "create-issue", 
            "--repo", "test-repo", 
            "--title", "Test Issue", 
            "--body", "Issue description", 
            "--labels", "bug", "enhancement",
            "--assignees", "user1", "user2"
        ]
        
        with patch.object(sys, "argv", ["imbizopm"] + test_args):
            args = parse_args()
            
        self.assertEqual(args.command, "create-issue")
        self.assertEqual(args.repo, "test-repo")
        self.assertEqual(args.title, "Test Issue")
        self.assertEqual(args.body, "Issue description")
        self.assertEqual(args.labels, ["bug", "enhancement"])
        self.assertEqual(args.assignees, ["user1", "user2"])
        
    def test_parse_args_ai_project(self):
        """Test parsing ai-project command arguments."""
        test_args = [
            "ai-project", 
            "--prompt", "Create a task manager", 
            "--repo", "task-manager",
            "--provider", "openai",
            "--model", "gpt-4",
            "--private",
            "--save-tasks", "tasks.json"
        ]
        
        with patch.object(sys, "argv", ["imbizopm"] + test_args):
            args = parse_args()
            
        self.assertEqual(args.command, "ai-project")
        self.assertEqual(args.prompt, "Create a task manager")
        self.assertEqual(args.repo, "task-manager")
        self.assertEqual(args.provider, "openai")
        self.assertEqual(args.model, "gpt-4")
        self.assertTrue(args.private)
        self.assertEqual(args.save_tasks, "tasks.json")
        
    @patch("json.load")
    @patch("builtins.open", new_callable=MagicMock)
    def test_load_issues_from_file(self, mock_open, mock_json_load):
        """Test loading issues from a JSON file."""
        test_issues = [
            {"title": "Issue 1", "body": "Description 1"},
            {"title": "Issue 2", "body": "Description 2"}
        ]
        mock_json_load.return_value = test_issues
        
        # Import the function directly for testing
        from imbizopm.cli import load_issues_from_file
        
        result = load_issues_from_file("issues.json")
        
        mock_open.assert_called_once_with("issues.json", "r")
        self.assertEqual(result, test_issues)
        
    @patch("json.load")
    @patch("builtins.open")
    def test_load_issues_from_file_error(self, mock_open, mock_json_load):
        """Test error handling when loading issues from an invalid file."""
        mock_json_load.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        # Import the function directly for testing
        from imbizopm.cli import load_issues_from_file
        
        with patch("sys.exit") as mock_exit:
            load_issues_from_file("invalid.json")
            mock_exit.assert_called_once_with(1)
            
    @patch("sys.exit")
    @patch("imbizopm.cli.parse_args")
    def test_main_no_command(self, mock_parse_args, mock_exit):
        """Test main function with no command specified."""
        mock_parse_args.return_value = MagicMock(command=None)
        
        main()
        
        mock_exit.assert_called_once_with(1)
        
    @patch("sys.exit")
    @patch("builtins.print")
    @patch("imbizopm.cli.parse_args")
    def test_main_create_repo(self, mock_parse_args, mock_print, mock_exit):
        """Test main function with create-repo command."""
        # Setup
        mock_args = MagicMock(
            command="create-repo",
            name="test-repo",
            description="Test repository",
            private=True,
            token="test_token"
        )
        mock_parse_args.return_value = mock_args
        
        self.mock_github_manager.create_repository.return_value = {
            "success": True,
            "repository": {
                "name": "test-repo",
                "url": "https://github.com/user/test-repo"
            }
        }
        
        # Execute
        main()
        
        # Assert
        self.mock_github_manager_class.assert_called_once_with(token="test_token")
        self.mock_github_manager.create_repository.assert_called_once_with(
            name="test-repo",
            description="Test repository",
            private=True
        )
        mock_exit.assert_not_called()  # Should not exit with error
        
    @patch("sys.exit")
    @patch("builtins.print")
    @patch("imbizopm.cli.parse_args")
    def test_main_create_repo_failure(self, mock_parse_args, mock_print, mock_exit):
        """Test main function with create-repo command that fails."""
        # Setup
        mock_args = MagicMock(
            command="create-repo",
            name="test-repo",
            token=None
        )
        mock_parse_args.return_value = mock_args
        
        self.mock_github_manager.create_repository.return_value = {
            "success": False,
            "error": "Repository already exists"
        }
        
        # Execute
        main()
        
        # Assert
        mock_exit.assert_called_once_with(1)
        
    @patch("sys.exit")
    @patch("builtins.print")
    @patch("builtins.input", return_value="Create a task manager app")
    @patch("imbizopm.cli.parse_args")
    @patch("imbizopm.cli.config")
    def test_main_ai_project_with_prompt_input(self, mock_config, mock_parse_args, mock_input, mock_print, mock_exit):
        """Test main function with ai-project command where prompt is entered via input."""
        # Setup
        mock_args = MagicMock(
            command="ai-project",
            prompt=None,
            provider="openai",
            model=None,
            dry_run=True,
            save_tasks="tasks.json",
            token=None,
            api_key=None
        )
        mock_parse_args.return_value = mock_args
        
        mock_config.get_llm_config.return_value = {"api_key": "test_key", "model": "gpt-4"}
        
        project_data = {
            "project_title": "Task Manager App",
            "project_description": "A web application for managing tasks",
            "tasks": []
        }
        self.mock_project_generator.interactive_project_creation.return_value = (project_data, [])
        
        # Execute
        with patch("builtins.open", new_callable=MagicMock) as mock_open:
            with patch("json.dump") as mock_json_dump:
                main()
                
                # Assert correct file writing
                mock_open.assert_called_once_with("tasks.json", "w")
                mock_json_dump.assert_called_once()
                
        # Assert
        mock_input.assert_called_once_with("Enter your project idea: ")
        self.mock_project_generator_class.assert_called_once_with("openai", **{"api_key": "test_key", "model": "gpt-4"})
        self.mock_project_generator.interactive_project_creation.assert_called_once_with("Create a task manager app")
        mock_exit.assert_called_once_with(0)  # Should exit with success due to dry_run
        
    @patch("sys.exit")
    @patch("builtins.print")
    @patch("imbizopm.cli.parse_args")
    def test_main_ai_project_with_github_creation(self, mock_parse_args, mock_print, mock_exit):
        """Test main function with ai-project command that creates GitHub resources."""
        # Setup
        mock_args = MagicMock(
            command="ai-project",
            prompt="Create a task manager",
            provider="openai",
            model="gpt-4",
            dry_run=False,
            save_tasks=None,
            repo="task-manager",
            private=True,
            token="test_token",
            api_key="test_api_key"
        )
        mock_parse_args.return_value = mock_args
        
        project_data = {
            "project_title": "Task Manager App",
            "project_description": "A web application for managing tasks"
        }
        issues = [
            {"title": "Setup project", "body": "Initialize repository", "labels": ["setup"]}
        ]
        self.mock_project_generator.interactive_project_creation.return_value = (project_data, issues)
        
        self.mock_github_manager.create_repository.return_value = {
            "success": True,
            "repository": {
                "name": "task-manager",
                "url": "https://github.com/user/task-manager"
            }
        }
        
        self.mock_github_manager.create_project.return_value = {
            "success": True,
            "project": {
                "name": "Task Manager App"
            }
        }
        
        self.mock_github_manager.create_issue.return_value = {
            "success": True,
            "issue": {
                "number": 1,
                "title": "Setup project"
            }
        }
        
        # Execute
        main()
        
        # Assert
        self.mock_project_generator_class.assert_called_once_with(
            "openai", 
            api_key="test_api_key", 
            model="gpt-4"
        )
        self.mock_github_manager_class.assert_called_once_with(token="test_token")
        self.mock_github_manager.create_repository.assert_called_once_with(
            name="task-manager",
            description="A web application for managing tasks",
            private=True
        )
        self.mock_github_manager.create_project.assert_called_once_with(
            repo_name="task-manager",
            project_name="Task Manager App",
            body="A web application for managing tasks"
        )
        self.mock_github_manager.create_issue.assert_called_once_with(
            repo_name="task-manager",
            title="Setup project",
            body="Initialize repository",
            labels=["setup"]
        )
        mock_exit.assert_called_once_with(0)  # Should exit with success
        
    @patch("sys.exit")
    @patch("imbizopm.cli.parse_args")
    def test_main_exception(self, mock_parse_args, mock_exit):
        """Test main function with an exception."""
        # Setup
        mock_args = MagicMock(command="create-repo", name="test-repo", token=None)
        mock_parse_args.return_value = mock_args
        
        # Make GitHubManager raise an exception
        self.mock_github_manager_class.side_effect = Exception("Test error")
        
        # Execute with captured stdout
        with patch("builtins.print") as mock_print:
            main()
        
        # Assert
        mock_print.assert_any_call("Error: Test error")
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
