"""
Two-step JSON generation utility based on research showing better results
when LLMs first generate free-form text, then convert to structured JSON.
"""

import json
from typing import Type

from langchain_core.language_models import BaseChatModel
from llm_output_parser import parse_json
from loguru import logger
from pydantic import BaseModel


class TwoStepJSONGenerator:
    """
    Implements two-step JSON generation:
    1. First step: Let the LLM generate free-form text response
    2. Second step: Use another LLM call to convert the text to structured JSON
    """

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def generate_text_then_json(
        self,
        system_prompt: str,
        user_input: str,
        target_model_class: Type[BaseModel],
        max_retries: int = 2,
    ) -> BaseModel:
        """
        Generate structured output using two-step approach.

        Args:
            system_prompt: The system prompt for the first step (free-form generation)
            user_input: The user input for the first step
            target_model_class: The Pydantic model class to structure the output
            max_retries: Maximum number of retries for JSON conversion

        Returns:
            Validated Pydantic model instance
        """
        # Step 1: Generate free-form text
        free_form_text = self._generate_free_form_text(system_prompt, user_input)

        # Step 2: Convert to structured JSON
        structured_output = self._convert_to_json(
            free_form_text, target_model_class, max_retries
        )

        return structured_output

    def _generate_free_form_text(self, system_prompt: str, user_input: str) -> str:
        """
        Step 1: Generate free-form text response without JSON constraints.
        """
        # Modified system prompt to encourage natural language response
        enhanced_system_prompt = f"""{system_prompt}

IMPORTANT: Respond in natural, free-flowing text. Do NOT format your response as JSON or any structured format. 
Just provide a clear, comprehensive answer that covers all the required information in a conversational manner.
Think through your response step by step and provide detailed explanations."""

        messages = [
            {"role": "system", "content": enhanced_system_prompt},
            {"role": "human", "content": user_input},
        ]

        response = self.llm.invoke(messages)
        free_form_text = response.content

        logger.debug(
            f"Generated free-form text (first {200} chars): {free_form_text[:200]}..."
        )
        return free_form_text

    def _convert_to_json(
        self, free_form_text: str, target_model_class: Type[BaseModel], max_retries: int
    ) -> BaseModel:
        """
        Step 2: Convert free-form text to structured JSON.
        """
        # Create an example of the target structure
        example_json = target_model_class.model_json_schema()
        example_instance = (
            target_model_class.example()
            if hasattr(target_model_class, "example")
            else {}
        )

        conversion_prompt = f"""You are a JSON conversion specialist. Your task is to convert the provided free-form text into a valid JSON structure.

TARGET JSON SCHEMA:
```json
{json.dumps(example_json, indent=2)}
```

EXAMPLE OUTPUT FORMAT:
```json
{json.dumps(example_instance, indent=2) if example_instance else "{}"}
```

INSTRUCTIONS:
1. Extract all relevant information from the free-form text
2. Structure it according to the target JSON schema
3. Ensure all required fields are populated
4. Use appropriate data types (strings, arrays, objects, etc.)
5. If information is missing, use reasonable defaults or empty values
6. Output ONLY valid JSON - no additional text or explanations

FREE-FORM TEXT TO CONVERT:
{free_form_text}

JSON OUTPUT:"""

        for attempt in range(max_retries + 1):
            try:
                messages = [{"role": "human", "content": conversion_prompt}]
                response = self.llm.invoke(messages)
                json_text = response.content.strip()

                # Parse the JSON
                parsed_json = parse_json(json_text)

                if "error" in parsed_json:
                    raise ValueError(f"JSON parsing error: {parsed_json['error']}")
                if len(parsed_json) == 1:
                    logger.debug("Single key JSON detected, extracting value")
                    logger.debug(f"Parsed JSON: {parsed_json}")
                    parsed_json = list(parsed_json.values())[0]

                # Validate against the Pydantic model
                validated_model = target_model_class.model_validate(parsed_json)

                logger.debug(
                    f"Successfully converted to structured JSON on attempt {attempt + 1}"
                )
                return validated_model

            except Exception as e:
                logger.warning(f"JSON conversion attempt {attempt + 1} failed: {e}")
                if attempt == max_retries:
                    logger.error(
                        f"Failed to convert to JSON after {max_retries + 1} attempts"
                    )
                    raise ValueError(
                        f"Failed to convert free-form text to structured JSON: {e}"
                    )
                else:
                    # For retry, add more specific instructions
                    conversion_prompt += f"\n\nPrevious attempt failed with error: {e}\nPlease ensure the JSON is valid and matches the schema exactly."

        # This should never be reached due to the raise in the loop
        raise ValueError("Unexpected error in JSON conversion")


def create_two_step_system_prompt(original_system_prompt: str) -> str:
    """
    Create a system prompt optimized for the two-step approach.
    Removes JSON formatting instructions and encourages natural language.
    """
    # Remove common JSON-related instructions
    json_keywords = [
        "json",
        "JSON",
        "structured format",
        "format your response",
        "```json",
        "output format",
        "structure your output",
    ]

    cleaned_prompt = original_system_prompt
    for keyword in json_keywords:
        if keyword.lower() in cleaned_prompt.lower():
            logger.debug(f"Cleaning JSON-related keyword from prompt: {keyword}")

    # Add natural language encouragement
    enhanced_prompt = f"""{cleaned_prompt}

RESPONSE STYLE: Provide your analysis and recommendations in clear, natural language. 
Think through each aspect thoroughly and explain your reasoning. Focus on being comprehensive 
and detailed rather than worrying about specific formatting."""

    return enhanced_prompt
