from typing import Any, Callable, Dict, Optional

from langchain_core.language_models import BaseChatModel
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent
from llm_output_parser import parse_json
from loguru import logger
from pydantic import BaseModel

from .config import AgentDtypes, AgentState


def extract_structured_data(text: str) -> Dict[str, Any]:
    """
    Extract structured data from agent response text.

    Args:
        text: The text output from an agent

    Returns:
        Dict with extracted structured data
    """
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
        model_class: Optional[Callable] = None,
        description: str = "",
    ):
        self.name = name
        self.description = description
        self.llm = llm
        self.model_class = model_class
        self.structured_output = model_class is not None
        self.system_prompt = system_prompt
        self.format_prompt = format_prompt
        self.agent: CompiledGraph = None
        self._build_agent()

    def _format_input(self, content: str) -> str:
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

    def _parse_content(self, content: str):
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
        model_name: BaseModel = getattr(AgentDtypes, self.name)
        try:
            return model_name.model_validate(parsed_content, strict=False)
        except Exception as e:
            logger.warning(f"Failed to validate output: {self.name}")
            logger.warning(f"Error: {e}")
            logger.warning(f"Parsed content: {parsed_content}")
            logger.warning(f"Raw content: {content}")
            if retry_text:
                logger.warning(f"Retry text: {retry_text}")
            raise ValueError(f"Failed to validate output: {self.name}")

    def run(self, state: AgentState) -> AgentState:
        raw_output = self.agent.invoke(
            {"messages": self._format_input(self._prepare_input(state))}
        )
        if self.structured_output:
            parsed_content: BaseModel = raw_output["structured_response"]
            logger.debug(parsed_content)
        else:
            parsed_content = self._parse_content(raw_output["messages"][-1].content)
        state["messages"] = raw_output["messages"]
        state[self.name] = parsed_content
        state["routes"] = [self.name]
        return self._process_result(state, parsed_content)

    def _prepare_input(self, state: AgentState) -> str:
        """Prepare input for the agent."""
        # Default implementation that can be overridden
        return state["messages"] if state["messages"] else state["input"]

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        """Process the agent result and update the state."""
        # Default implementation that can be overridden
        return state
