from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..base_agent import AgentState, BaseAgent
from ..dtypes.negotiator_types import ConflictResolution
from ..prompts.negotiator_prompts import (
    get_negotiator_output_format,
    get_negotiator_prompt,
)
from .config import AgentDtypes, AgentRoute


class NegotiatorAgent(BaseAgent):
    """Agent that coordinates conflict resolution among agents."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.NegotiatorAgent,
            get_negotiator_output_format(),
            get_negotiator_prompt(),
            ConflictResolution if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        # Identify which aspect has conflicts
        return f"""# Project Idea
{state[AgentRoute.ClarifierAgent].refined_idea}
        
# Scoper Agent
{dumps_to_yaml(state[AgentRoute.ScoperAgent])}

# Planner Agent
{dumps_to_yaml(state[AgentRoute.PlannerAgent].components)}


Consider the main idea, plan and scope. Identify any conflicts or inconsistencies between them."""

    def _process_result(
        self, state: AgentState, result: AgentDtypes.NegotiatorAgent
    ) -> AgentState:
        state["forward"] = (
            AgentRoute.ScoperAgent
            if result.conflict_area == "scope"
            else AgentRoute.PlannerAgent
        )
        state["backward"] = AgentRoute.NegotiatorAgent
        return state
