from typing import Annotated, Any, Callable, Dict, Optional, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.graph import CompiledGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from llm_output_parser import parse_json
from loguru import logger
from pydantic import BaseModel
from typing_extensions import TypedDict

from .agents.config import AgentDtypes


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


class AgentState(TypedDict):
    input: str
    start: str
    backward: str
    forward: str
    warn_errors: dict[str, Any]
    routes: Annotated[list[str], add_messages]
    messages: Annotated[list[str], add_messages]
    ClarifierAgent: AgentDtypes.ClarifierAgent
    OutcomeAgent: AgentDtypes.OutcomeAgent
    PlannerAgent: AgentDtypes.PlannerAgent
    ScoperAgent: AgentDtypes.ScoperAgent
    TaskifierAgent: AgentDtypes.TaskifierAgent
    TimelineAgent: AgentDtypes.TimelineAgent
    RiskAgent: AgentDtypes.RiskAgent
    ValidatorAgent: AgentDtypes.ValidatorAgent
    PMAdapterAgent: AgentDtypes.PMAdapterAgent
    NegotiatorAgent: AgentDtypes.NegotiatorAgent


class BaseAgent:
    """Base agent class with React pattern support."""

    def __init__(
        self,
        llm: BaseChatModel,
        name: str,
        system_prompt: str,
        format_prompt: str,
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

    def _build_agent(self):
        """Build the React agent."""
        messges = [
            ("system", self.system_prompt),
            (
                "human",
                "Here is some additionnal information to into account:\n\n{messages}",
            ),
        ]
        if self.structured_output:
            messges.append(
                (
                    "system",
                    self.format_prompt
                    + "\n\nFormat your response as JSON (strictly output only the JSON, choose the appropriate format)",
                )
            )
        prompt = ChatPromptTemplate.from_messages(messges)

        self.agent: CompiledGraph = create_react_agent(
            self.llm, tools=[], prompt=prompt, response_format=self.model_class
        )

    def _parse_content(self, content: str):
        parsed_content = extract_structured_data(content)
        retry_text = None
        if "error" in parsed_content:
            logger.warning(f"Errors found in output: {self.name}")
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
        raw_output = self.agent.invoke({"messages": self._prepare_input(state)})
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
