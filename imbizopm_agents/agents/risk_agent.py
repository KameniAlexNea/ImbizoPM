from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import FeasibilityAssessment
from ..prompts.risk_prompts import get_risk_output_format, get_risk_prompt
from .base_agent import AgentDtypes, AgentState, BaseAgent
from .config import AgentRoute


class RiskAgent(BaseAgent):
    """Agent that reviews feasibility and spots contradictions."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.RiskAgent,
            get_risk_output_format(),
            get_risk_prompt(),
            FeasibilityAssessment if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""# Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent], indent=4)}

# Plan Agent
{dumps_to_yaml(state[AgentRoute.PlannerAgent].components, indent=4)}

# Taskifier Agent
{dumps_to_yaml(state[AgentRoute.TaskifierAgent].tasks, indent=4)}

# Timeline Agent
{dumps_to_yaml(state[AgentRoute.TimelineAgent], indent=4)}

Assess risks and overall feasibility. You should output a JSON format"""

    def _process_result(
        self, state: AgentState, result: AgentDtypes.RiskAgent
    ) -> AgentState:
        # Move instead of planning to negotiate
        state["forward"] = (
            AgentRoute.ValidatorAgent
            if result.feasible or not result.dealbreakers
            else AgentRoute.PlannerAgent
        )
        state["backward"] = AgentRoute.RiskAgent
        return state
