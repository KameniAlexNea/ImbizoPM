"""
This class is now merged with Clarifier Agent
"""

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..base_agent import AgentDtypes, AgentState, BaseAgent
from ..dtypes.outcome_types import ProjectSuccessCriteria
from ..prompts.outcome_prompts import (
    get_outcome_output_format,
    get_outcome_prompt,
)
from .config import AgentRoute


class OutcomeAgent(BaseAgent):
    """Agent that defines success metrics and deliverables."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.OutcomeAgent,
            get_outcome_output_format(),
            get_outcome_prompt(),
            ProjectSuccessCriteria if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""# Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent])}

Define success metrics and deliverables."""

    def _process_result(
        self, state: AgentState, result: AgentDtypes.OutcomeAgent
    ) -> AgentState:
        # Determine next step based on presence of outcomes
        state["forward"] = (
            AgentRoute.PlannerAgent
            if result.success_metrics
            else AgentRoute.ClarifierAgent
        )
        state["backward"] = AgentRoute.OutcomeAgent

        return state
