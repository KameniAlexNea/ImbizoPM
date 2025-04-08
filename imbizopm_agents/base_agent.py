from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent


class AgentState(TypedDict):
    input: str
    idea: Dict[str, Any]
    goals: List[str]
    constraints: List[str]
    outcomes: List[str]
    deliverables: List[Dict[str, Any]]
    plan: Dict[str, Any]
    scope: Dict[str, Any]
    tasks: List[Dict[str, Any]]
    timeline: Dict[str, Any]
    risks: List[Dict[str, Any]]
    validation: Dict[str, bool]
    messages: List[BaseMessage]
    next: Optional[str]


class BaseAgent:
    """Base agent class with React pattern support."""

    def __init__(
        self,
        llm: BaseChatModel,
        name: str,
        system_prompt: str,
        description: str = "",
    ):
        self.name = name
        self.description = description
        self.llm = llm
        self.system_prompt = system_prompt
        self.agent: CompiledGraph = None
        self._build_agent()

    def _build_agent(self):
        """Build the React agent."""
        prompt = ChatPromptTemplate.from_messages(
            [("system", self.system_prompt), ("human", "{input}")]
        )

        self.agent: CompiledGraph = create_react_agent(self.llm, tools=[], prompt=prompt)

    def run(self, state: AgentState) -> AgentState:
        """Run the agent on the current state."""
        # Default implementation that can be overridden
        result = self.agent.invoke({"input": self._prepare_input(state)})

        # Update messages
        if "messages" in result:
            state["messages"] = result["messages"]

        return self._process_result(state, result)

    def _prepare_input(self, state: AgentState) -> str:
        """Prepare input for the agent."""
        # Default implementation that can be overridden
        return state["input"]

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        """Process the agent result and update the state."""
        # Default implementation that can be overridden
        return state
