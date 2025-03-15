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

For AI-powered project generation, you'll need an API key for your preferred LLM provider:

```bash
# For OpenAI
export OPENAI_API_KEY=your_openai_api_key

# For Anthropic
export ANTHROPIC_API_KEY=your_anthropic_api_key

# For Ollama (local setup)
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3
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

### AI-Powered Project Creation

Generate a project structure using an AI model and create it on GitHub:

```bash
imbizopm ai-project --prompt "Create a task management application with user authentication"
```

With specific provider:

```bash
imbizopm ai-project --provider openai --model gpt-4 --prompt "Create a Python web scraper with proxy rotation"
```

Generate without creating on GitHub:

```bash
imbizopm ai-project --prompt "Create a mobile app for tracking fitness" --dry-run --save-tasks project-tasks.json
```

Available LLM providers:

- `openai`: OpenAI GPT models (requires OPENAI_API_KEY)
- `anthropic`: Anthropic Claude models (requires ANTHROPIC_API_KEY)
- `ollama`: Local Ollama models (requires Ollama running locally or specified OLLAMA_BASE_URL)

## License

MIT
