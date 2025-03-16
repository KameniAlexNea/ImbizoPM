# Configuration System

ImbizoPM uses a centralized configuration system to manage settings and provide consistent access to model configurations, API keys, and other parameters across the application.

## Overview

The configuration system consists of two main components:

1. `config.py` - Provides the central `Config` class and a global `config` instance
2. `model_config.py` - Provides specialized configuration classes for LLM providers and models

## Usage

### Basic Usage

Always import and use the central `config` instance:

```python
from imbizopm.config import config

# Access environment variables
github_token = config.github_token

# Access model configurations
openai_model = config.openai_model
anthropic_api_key = config.anthropic_api_key
```

### LLM Provider Configuration

To get configuration for a specific provider:

```python
provider_config = config.get_llm_config('openai')
# Returns: {'api_key': '...', 'model': 'gpt-4'}
```

### Access Model Information

To access model information:

```python
# Get default model for a provider
default_model_name = config.models.openai.default_model.name

# Get all available models for a provider
model_names = config.models.get_provider_model_names('anthropic')

# Get specific provider configuration
provider_config = config.models.get_provider_config('ollama')
```

## Environment Variables

The following environment variables are supported:

- `GITHUB_TOKEN` - GitHub personal access token
- `OPENAI_API_KEY` - API key for OpenAI
- `ANTHROPIC_API_KEY` - API key for Anthropic
- `OLLAMA_BASE_URL` - Base URL for Ollama (defaults to "http://localhost:11434")
- `MASTER_PROVIDER` - Default master provider for aggregation operations (defaults to "openai")

These can be set in a `.env` file in the project root or directly in the environment.

## Model Configuration

The model configuration system provides:

- Lists of available models for each provider
- Default model settings
- Context length information
- Model capabilities

Each provider (OpenAI, Anthropic, Ollama) has its own configuration class with appropriate defaults.
