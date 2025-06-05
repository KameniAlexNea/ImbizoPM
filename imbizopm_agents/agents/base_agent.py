from typing import Any, Callable, Dict, List, Optional, Type, Union

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent
from llm_output_parser import parse_json
from loguru import logger
from pydantic import BaseModel

from ..utilities.two_step_json import (
    TwoStepJSONGenerator,
    create_two_step_system_prompt,
)
from .config import AgentDtypes, AgentState


def extract_structured_data(text: str) -> Dict[str, Any]:
    try:
        return parse_json(text)
    except Exception as e:
        return {"text": text, "error": str(e)}


class BaseAgent:
    """Base agent class with React pattern support."""

    def __init__(
        self,
        llm: BaseChatModel,
        name: str,
        format_prompt: str,
        system_prompt: str,
        model_class: Optional[Type[BaseModel]] = None,
        description: str = "",
        prepare_input: Optional[Callable[[AgentState], str]] = None,
        process_result: Optional[Callable[[AgentState, Any], AgentState]] = None,
        next_step: Optional[Callable[[AgentState, Any], Union[str, str]]] = None,
        use_two_step_generation: bool = True,
    ):
        self.name = name
        self.description = description
        self.llm = llm
        self.model_class = model_class
        self.structured_output = model_class is not None
        self.use_two_step_generation = use_two_step_generation
        self.system_prompt = system_prompt
        self.format_prompt = format_prompt

        # Initialize two-step JSON generator if needed
        if self.use_two_step_generation and self.model_class:
            self.two_step_generator = TwoStepJSONGenerator(llm)
            # Create optimized system prompt for two-step generation
            self.two_step_system_prompt = create_two_step_system_prompt(system_prompt)
        else:
            self.two_step_generator = None
            self.two_step_system_prompt = system_prompt
        self.prepare_input: Callable[[AgentState], str] = (
            prepare_input or self._default_prepare_input
        )
        self.process_result: Callable[[AgentState, Any], AgentState] = (
            process_result or self._default_process_result
        )
        self.next_step: Callable[[AgentState, Any], Union[str, str]] = (
            next_step or self._default_next_step
        )
        self.agent: CompiledGraph = None
        self._build_agent()

    def _default_prepare_input(self, state: AgentState) -> str:
        """Default input preparation logic."""
        return (
            state.get("messages")[-1].content
            if state.get("messages")
            else state["input"]
        )

    def _default_process_result(self, state: AgentState, result: Any) -> AgentState:
        """Default result processing logic (minimal)."""
        return state

    def _default_next_step(self, state: AgentState, result: Any) -> str:
        """Default next step logic."""
        return END

    def _format_input(self, content: str) -> List[Dict[str, str]]:
        text = f"======= Input Data =======\n{content}" + (
            ""
            if self.structured_output
            else f"\n\n\n======= Output Data =======\n{self.format_prompt}"
        )
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "human", "content": text},
        ]

    def _build_agent(self):
        """Build the React agent."""
        self.agent: CompiledGraph = create_react_agent(
            self.llm, tools=[], prompt=None, response_format=self.model_class
        )

    def _parse_content(self, content: str) -> BaseModel:
        parsed_content = extract_structured_data(content)
        retry_text = None
        if "error" in parsed_content:
            logger.error(f"Errors found in output: {self.name}. Retrying...")
            logger.error(f"Error: {parsed_content['error']}")
            messages = [
                {
                    "role": "human",
                    "content": f"Format the following text as JSON (strictly output only the JSON, choose the appropriate format):\n{content}"
                    + self.format_prompt,
                }
            ]
            retry_text = self.llm.invoke(messages).content
            parsed_content = extract_structured_data(retry_text)
            if "error" in parsed_content:
                raise ValueError(f"Failed to parse output again: {self.name}")
        model_type: Type[BaseModel] = getattr(AgentDtypes, self.name)
        try:
            return model_type.model_validate(parsed_content, strict=False)
        except Exception as e:
            logger.warning(f"Failed to validate output: {self.name}")
            logger.warning(f"Error: {e}")
            logger.warning(f"Parsed content: {parsed_content}")
            logger.warning(f"Raw content: {content}")
            if retry_text:
                logger.warning(f"Retry text: {retry_text}")
            raise ValueError(f"Failed to validate output: {self.name}")

    def run(self, state: AgentState) -> AgentState:
        """Executes the agent's logic."""
        input_content = self.prepare_input(state)
        logger.debug(f"Running agent {self.name} with input:\n{input_content}")

        # Choose generation approach based on configuration
        if self.use_two_step_generation and self.model_class:
            # Use two-step generation: text first, then JSON
            logger.debug(f"Using two-step generation for {self.name}")
            parsed_content = self.two_step_generator.generate_text_then_json(
                system_prompt=self.two_step_system_prompt,
                user_input=input_content,
                target_model_class=self.model_class,
            )
            # Create mock messages for consistency with existing flow
            raw_output = {
                "messages": [
                    {"role": "system", "content": self.two_step_system_prompt},
                    {"role": "human", "content": input_content},
                    {
                        "role": "assistant",
                        "content": f"Generated structured output for {self.name}",
                    },
                ]
            }
            logger.debug(
                f"Two-step generation completed for {self.name}: {parsed_content}"
            )
        else:
            # Use original approach
            raw_output = self.agent.invoke(
                {"messages": self._format_input(input_content)}
            )

            if self.structured_output:
                parsed_content: BaseModel = raw_output["structured_response"]
                logger.debug(
                    f"Structured output received for {self.name}: {parsed_content}"
                )
            else:
                raw_text_output = raw_output["messages"][-1].content
                parsed_content = self._parse_content(raw_text_output)
                logger.debug(f"Parsed output for {self.name}: {parsed_content}")

        state["messages"] = raw_output["messages"]
        state[self.name] = parsed_content
        state["routes"] = state.get("routes", []) + [self.name]

        next_node = self.next_step(state, parsed_content)
        state["forward"] = next_node
        logger.debug(f"Agent {self.name} determined next step: {state['forward']}")

        processed_state = self.process_result(state, parsed_content)

        return processed_state
