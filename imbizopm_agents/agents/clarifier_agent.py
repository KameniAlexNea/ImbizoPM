from typing import Any, Dict

from langchain_core.language_models import BaseChatModel

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import ProjectPlan
from ..prompts.clarifier_prompts import (
    get_clarifier_output_format,
    get_clarifier_prompt,
)
from .base_agent import AgentState, BaseAgent
from .config import AgentRoute


class ClarifierAgent(BaseAgent):
    """Agent that refines the idea, extracts goals, scope, and constraints."""

    def __init__(self, llm: BaseChatModel, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.ClarifierAgent,
            get_clarifier_output_format(),
            get_clarifier_prompt(),
            ProjectPlan if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        """Prepare input for the agent."""
        if state.get("backward") is not None:
            backward = state.get("backward")
            if backward == AgentRoute.PlannerAgent:  # From planner agent
                return f"""
idea: {state['input']}

# Previous Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent])}

# Previous Planner Agent
{dumps_to_yaml(state[AgentRoute.PlannerAgent].vague_details)}

From the previous refined idea, goals, constraints, it was not possible to extract clear phases, epics, and strategies. Please clarify the project idea, goals, and constraints.
"""
            elif backward == AgentRoute.TaskifierAgent or (
                AgentRoute.TaskifierAgent in state
                and state[AgentRoute.TaskifierAgent] is not None
            ):
                return f"""
idea: {state['input']}

# Previous Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent])}

# Previous Planner Agent
{dumps_to_yaml(state[AgentRoute.PlannerAgent].components)}

# Taskifier Agent
{dumps_to_yaml(state[AgentRoute.TaskifierAgent].missing_info_details)}

From the previous refined idea, goals, constraints, it was not possible to extract clear tasks. Please clarify the project idea, goals, and constraints.
"""
        return state["input"]

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["forward"] = AgentRoute.PlannerAgent
        state["backward"] = AgentRoute.ClarifierAgent
        return state
