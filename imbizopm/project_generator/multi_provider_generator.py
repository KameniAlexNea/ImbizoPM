"""
Multi-provider project generator that uses multiple LLM providers and aggregates their outputs.
"""

import concurrent.futures
import json
from typing import Dict, List, Optional, Union

from ..llm_providers import LLMProvider, get_llm_provider
from .project_generator import ProjectGenerator
from .prompts import project_description_prompt, tasks_generation_prompt


class MultiProviderProjectGenerator(ProjectGenerator):
    """
    Extended Project Generator that uses multiple LLM providers and aggregates their outputs.
    
    This class allows parallel generation of content from multiple providers and 
    uses a designated "master" provider to aggregate the results.
    """
    
    def __init__(
        self, 
        providers: List[Union[str, LLMProvider]], 
        master_provider_idx: int = 0,
        provider_kwargs: Optional[List[Dict]] = None
    ):
        """
        Initialize with multiple LLM providers.
        
        Args:
            providers: List of provider names or LLMProvider instances
            master_provider_idx: Index of the provider to use for aggregation (default: 0)
            provider_kwargs: List of provider-specific configuration dictionaries
                            (must match length of providers if provided)
        """
        if provider_kwargs and len(providers) != len(provider_kwargs):
            raise ValueError("providers and provider_kwargs must have the same length")
            
        # Initialize all providers
        self.llm_providers = []
        for i, provider in enumerate(providers):
            kwargs = provider_kwargs[i] if provider_kwargs else {}
            if isinstance(provider, str):
                self.llm_providers.append(get_llm_provider(provider, **kwargs))
            else:
                self.llm_providers.append(provider)
                
        # Set the master provider for aggregation
        if not 0 <= master_provider_idx < len(self.llm_providers):
            raise ValueError(f"master_provider_idx must be between 0 and {len(self.llm_providers)-1}")
            
        self.master_provider_idx = master_provider_idx
        self.llm = self.llm_providers[master_provider_idx]  # Set master provider as default
        
    def generate_project_description(self, project_prompt: str) -> str:
        """
        Generate a project description using multiple providers and aggregate results.
        
        Args:
            project_prompt: User's prompt describing the project idea
            
        Returns:
            Aggregated project description
        """
        # Get descriptions from all providers in parallel
        descriptions = self._parallel_generate(
            [project_description_prompt(project_prompt)] * len(self.llm_providers)
        )
        
        # If only one provider, return its result directly
        if len(descriptions) == 1:
            return descriptions[0]
            
        # Aggregate the descriptions using the master provider
        return self._aggregate_descriptions(descriptions, project_prompt)
    
    def generate_tasks(self, project_description: str) -> Dict:
        """
        Generate task lists from multiple providers and aggregate results.
        
        Args:
            project_description: The finalized project description
            
        Returns:
            Aggregated task dictionary
        """
        # Get task lists from all providers in parallel
        task_responses = self._parallel_generate(
            [tasks_generation_prompt(project_description)] * len(self.llm_providers)
        )
        
        # Process each response to extract JSON
        task_lists = []
        for response in task_responses:
            try:
                # First try direct JSON parsing
                task_list = json.loads(response)
                task_lists.append(task_list)
            except json.JSONDecodeError:
                # If that fails, try to clean up the response
                try:
                    clean_response = self._clean_json_response(response)
                    task_list = json.loads(clean_response)
                    task_lists.append(task_list)
                except (json.JSONDecodeError, ValueError):
                    # If still fails, skip this response
                    continue
        
        # If only one valid task list, return it
        if len(task_lists) == 1:
            return task_lists[0]
            
        # If multiple task lists, aggregate them
        return self._aggregate_tasks(task_lists, project_description)
    
    def _parallel_generate(self, prompts: List[str]) -> List[str]:
        """
        Generate text from multiple providers in parallel.
        
        Args:
            prompts: List of prompts to send to providers
            
        Returns:
            List of responses from providers
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all generation tasks
            futures = [
                executor.submit(provider.generate_text, prompt)
                for provider, prompt in zip(self.llm_providers, prompts)
            ]
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error in provider: {e}")
                    # Add an empty result to maintain index alignment
                    results.append("")
        
        return results
    
    def _aggregate_descriptions(self, descriptions: List[str], original_prompt: str) -> str:
        """
        Aggregate multiple descriptions into one using the master provider.
        
        Args:
            descriptions: List of project descriptions
            original_prompt: Original user prompt
            
        Returns:
            Aggregated description
        """
        # Filter out empty descriptions
        valid_descriptions = [desc for desc in descriptions if desc.strip()]
        
        if not valid_descriptions:
            raise ValueError("No valid descriptions to aggregate")
            
        # If only one valid description, return it
        if len(valid_descriptions) == 1:
            return valid_descriptions[0]
        
        # Create a prompt for the master provider to aggregate descriptions
        aggregation_prompt_text = f"""
        I have received multiple project descriptions for the same project idea:
        
        Original project idea: {original_prompt}
        
        Description 1:
        {valid_descriptions[0]}
        
        """
        
        # Add additional descriptions
        for i, desc in enumerate(valid_descriptions[1:], 2):
            aggregation_prompt_text += f"""
            Description {i}:
            {desc}
            
            """
            
        aggregation_prompt_text += """
        Please create a comprehensive project description that combines the best elements
        from all these descriptions. The final description should be well-structured,
        comprehensive, and cover all important aspects of the project.
        """
        
        # Use the master provider to generate the aggregated description
        return self.llm.generate_text(aggregation_prompt_text)
    
    def _aggregate_tasks(self, task_lists: List[Dict], project_description: str) -> Dict:
        """
        Aggregate multiple task lists into one using the master provider.
        
        Args:
            task_lists: List of task dictionaries
            project_description: Original project description
            
        Returns:
            Aggregated task dictionary
        """
        # Filter out empty task lists
        valid_task_lists = [tl for tl in task_lists if tl.get("tasks")]
        
        if not valid_task_lists:
            raise ValueError("No valid task lists to aggregate")
            
        # If only one valid task list, return it
        if len(valid_task_lists) == 1:
            return valid_task_lists[0]
        
        # Convert task lists to formatted JSON strings for the prompt
        formatted_task_lists = []
        for i, tl in enumerate(valid_task_lists):
            formatted_task_lists.append(f"Task List {i+1}:\n```json\n{json.dumps(tl, indent=2)}\n```")
        
        # Create a prompt for the master provider to aggregate task lists
        task_aggregation_prompt = f"""
        I have received multiple task lists for the same project:
        
        Project description:
        {project_description}
        
        {'\n\n'.join(formatted_task_lists)}
        
        Please create a comprehensive task list that combines the best elements from all these lists.
        Include all important tasks while avoiding duplication. Make sure to maintain the structure
        with main tasks and subtasks, and include complexity and labels for each.
        
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
        
        # Use the master provider to generate the aggregated task list
        response = self.llm.generate_text(task_aggregation_prompt)
        
        # Extract and parse the JSON
        try:
            clean_response = self._clean_json_response(response)
            return json.loads(clean_response)
        except (json.JSONDecodeError, ValueError) as e:
            # If aggregation fails, return the first valid task list
            print(f"Error aggregating tasks: {e}")
            return valid_task_lists[0]
