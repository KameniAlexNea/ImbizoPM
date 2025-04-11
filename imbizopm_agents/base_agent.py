from typing import Annotated, Any, Callable, Dict, List, Optional, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.graph import CompiledGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from loguru import logger
from pydantic import BaseModel
from typing_extensions import TypedDict

from imbizopm_agents.dtypes.clarifier_types import ProjectPlan
from imbizopm_agents.dtypes.negotiator_types import ConflictResolution
from imbizopm_agents.dtypes.outcome_types import ProjectSuccessCriteria
from imbizopm_agents.dtypes.planner_types import ProjectPlanOutput
from imbizopm_agents.dtypes.pm_adapter_types import ProjectSummary
from imbizopm_agents.dtypes.risk_types import FeasibilityAssessment
from imbizopm_agents.dtypes.scoper_types import ScopeDefinition
from imbizopm_agents.dtypes.taskifier_types import TaskPlan
from imbizopm_agents.dtypes.timeline_types import ProjectTimeline
from imbizopm_agents.dtypes.validator_types import PlanValidation
from imbizopm_agents.utils import extract_structured_data


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
    messages: Annotated[list, add_messages]
    next: Optional[str]
    current: Optional[str]
    warn_errors: dict[str, Any]
    assumptions: list[str]
    feasibility_concerns: list[Dict[str, Any]]

class AgentState(TypedDict):
    start: str
    prev: str
    warn_errors: dict[str, Any]
    routes: Annotated[list[str], add_messages]
    ClarifierAgent: ProjectPlan
    OutcomeAgent: ProjectSuccessCriteria
    PlannerAgent: ProjectPlanOutput
    ScoperAgent: ScopeDefinition
    TaskifierAgent: TaskPlan
    TimelineAgent: ProjectTimeline
    RiskAgent: FeasibilityAssessment
    ValidatorAgent: PlanValidation
    PMAdapterAgent: ProjectSummary
    NegotiatorAgent: ConflictResolution


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
        if self.structured_output:
            self.system_prompt = self.system_prompt.replace(
                self.format_prompt,
                "Your output should follow exactly the schema provided in the format prompt.",
            ).strip()
        self._build_agent()

    def _build_agent(self):
        """Build the React agent."""
        prompt = ChatPromptTemplate.from_messages(
            [("system", self.system_prompt), ("human", "{messages}")]
        )

        self.agent: CompiledGraph = create_react_agent(
            self.llm, tools=[], prompt=prompt, response_format=self.model_class
        )

    def run(self, state: AgentState) -> AgentState:
        raw_output = self.agent.invoke({"messages": self._prepare_input(state)})
        if self.structured_output:
            content: BaseModel = raw_output["structured_response"]
            logger.debug(f"Structured output: {content}")
            parsed_content = content.model_dump()
        else:
            parsed_content = extract_structured_data(raw_output["messages"][-1].content)
        if "error" in parsed_content:
            logger.warning(f"Errors found in output: {self.name}")
            retry_text = self.llm.invoke(
                [
                    {
                        "role": "human",
                        "content": f"Format the following text as JSON (strictly output only the JSON, choose the appropriate format):\n{raw_output['messages'][-1].content}"
                        + self.format_prompt,
                    }
                ]
            ).content
            parsed_content = extract_structured_data(retry_text)
            if "error" in parsed_content:
                logger.error(f"Failed to parse output again: {self.name}")
                parsed_content["text"] = raw_output["messages"][-1].content
        state["messages"] = raw_output["messages"]
        return self._process_result(state, parsed_content)

    def _prepare_input(self, state: AgentState) -> str:
        """Prepare input for the agent."""
        # Default implementation that can be overridden
        return state["messages"] if state["messages"] else state["input"]

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        """Process the agent result and update the state."""
        # Default implementation that can be overridden
        return state
