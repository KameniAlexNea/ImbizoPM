# ImbizoPM

ImbizoPM is a tool to help you get started with your GitHub projects by automating the creation of repositories, projects, and issues.

## Installation

```bash
# Clone the repository
git clone https://github.com/KameniAlexNea/ImbizoPM.git
cd ImbizoPM

# Install the package
pip install -e .
```

## Configuration

Set your GitHub Personal Access Token as an environment variable:

```bash
export GITHUB_TOKEN=your_github_token
```

Alternatively, you can create a `.env` file in the root directory:

```
GITHUB_TOKEN=your_github_token
```

## Usage

### Creating a Repository

```bash
imbizopm create-repo --name my-awesome-project --description "This is an awesome project"
```

### Creating a Project Board

```bash
imbizopm create-project --repo my-awesome-project --name "Version 1.0" --description "First release of the project"
```

### Creating an Issue

```bash
imbizopm create-issue --repo my-awesome-project --title "Implement feature X" --body "We need to implement feature X with these requirements..."
```

### Creating a Project with Issues

Create a JSON file with issue definitions:

```json
[
  {
    "title": "Setup project structure",
    "body": "Create the initial project structure with necessary folders and files",
    "labels": ["documentation", "good first issue"]
  },
  {
    "title": "Implement core functionality",
    "body": "Implement the core functionality of the application",
    "labels": ["enhancement"]
  }
]
```

Then run:

```bash
imbizopm create-full-project --repo my-awesome-project --project-name "Sprint 1" --issues-file issues.json
```

## License

MIT
