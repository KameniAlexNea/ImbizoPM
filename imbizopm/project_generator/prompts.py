"""
Prompts module containing templates for various LLM prompts used in the ImbizoPM system.
"""

from ..config import config


def project_description_prompt(project_prompt: str) -> str:
    """
    Get prompt template for generating a project description.

    Args:
        project_prompt: User's prompt describing the project idea

    Returns:
        Complete prompt for the LLM
    """
    return f"""
    Based on the following project idea, generate a comprehensive project description. 
    The description should include:
    - A clear project title
    - Project overview and purpose
    - Main features and functionalities
    - Technology stack suggestions

    Project idea: {project_prompt}
    """


def project_refinement_prompt(original_description: str, user_feedback: str) -> str:
    """
    Get prompt template for refining a project description.

    Args:
        original_description: The original generated description
        user_feedback: User's feedback on how to improve the description

    Returns:
        Complete prompt for the LLM
    """
    return f"""
    Here is a project description:
    ---
    {original_description}
    ---

    The user has provided the following feedback to improve the description:
    ---
    {user_feedback}
    ---

    Please revise the project description according to the feedback and provide an improved version.
    """


def tasks_generation_prompt(project_description: str) -> str:
    """
    Get prompt template for generating tasks based on project description.

    Args:
        project_description: The finalized project description

    Returns:
        Complete prompt for the LLM
    """
    return f"""
    Based on the following project description, create a structured list of tasks and subtasks for project implementation.
    
    Project description:
    ---
    {project_description}
    ---
    
    Please organize the tasks in a hierarchical structure with main tasks and their subtasks.
    For each task, provide:
    1. A clear title
    2. A brief description
    3. Estimated complexity (Low, Medium, High)
    4. Labels for GitHub issues (like "enhancement", "documentation", "bug", etc.)
    
    Format your response as a JSON object with the following structure:
    {{
        "project_title": "Title extracted from description",
        "project_description": "A concise version of the project description",
        "tasks": [
            {{
                "title": "Task 1 title",
                "description": "Task 1 description",
                "complexity": "Medium",
                "labels": ["enhancement"],
                "subtasks": [
                    {{
                        "title": "Subtask 1.1 title",
                        "description": "Subtask 1.1 description",
                        "complexity": "Low",
                        "labels": ["documentation"]
                    }}
                ]
            }}
        ]
    }}
    
    Ensure the tasks cover all aspects of the project, including setup, core features, testing, and documentation.
    """


def aggregation_prompt(descriptions: list, original_prompt: str) -> str:
    """
    Get prompt template for aggregating multiple project descriptions.

    Args:
        descriptions: List of project descriptions from different providers
        original_prompt: The original user prompt

    Returns:
        Complete prompt for the master LLM to aggregate descriptions
    """
    prompt = f"""
    I have received multiple project descriptions for the same project idea:

    Original project idea: {original_prompt}

    """

    for i, description in enumerate(descriptions, 1):
        prompt += f"""
        Description {i}:
        ---
        {description}
        ---

        """

    prompt += """
    Please create a comprehensive project description that combines the best elements
    from all these descriptions. The final description should be well-structured,
    comprehensive, and cover all important aspects of the project.
    """

    return prompt


def task_aggregation_prompt(task_lists: list, project_description: str) -> str:
    """
    Get prompt template for aggregating multiple task lists.

    Args:
        task_lists: List of formatted task list strings
        project_description: The project description

    Returns:
        Complete prompt for the master LLM to aggregate task lists
    """
    task_lists_format = "\n\n".join(task_lists)

    # Use master model capabilities to improve task aggregation
    master_provider = config.master_provider
    master_model = config.models.get_provider_config(master_provider).default_model.name

    return f"""
    I have received multiple task lists for the same project:
    
    Project description:
    {project_description}
    
    {task_lists_format}
    
    Please create a comprehensive task list that combines the best elements from all these lists.
    Include all important tasks while avoiding duplication. Make sure to maintain the structure
    with main tasks and subtasks, and include complexity and labels for each.
    
    You are using {master_provider}'s {master_model} model to produce this aggregation.
    Focus on generating high-quality structured output.
    
    Return only a valid JSON object with the following structure:
    {{
        "project_title": "Title from description",
        "project_description": "A concise version of the project description",
        "tasks": [
            {{
                "title": "Task 1 title",
                "description": "Task 1 description",
                "complexity": "Medium",
                "labels": ["enhancement"],
                "subtasks": [
                    {{
                        "title": "Subtask 1.1 title",
                        "description": "Subtask 1.1 description",
                        "complexity": "Low",
                        "labels": ["documentation"]
                    }}
                ]
            }}
        ]
    }}
    """
