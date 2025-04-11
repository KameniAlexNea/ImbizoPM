import json
from typing import Any, Dict

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..base_agent import AgentState, BaseAgent, AgentDtypes
from ..dtypes.risk_types import FeasibilityAssessment
from ..prompts.risk_prompts import get_risk_output_format, get_risk_prompt
from ..agent_routes import AgentRoute

RISK_OUTPUT = get_risk_output_format()

RISK_PROMPT = get_risk_prompt()


class RiskAgent(BaseAgent):
    """Agent that reviews feasibility and spots contradictions."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            "Risk",
            RISK_PROMPT,
            RISK_OUTPUT,
            FeasibilityAssessment if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""# Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent], indent=2)}

# Plan Agent
{dumps_to_yaml(state[AgentRoute.PlannerAgent], indent=2)}

# Taskifier Agent
{dumps_to_yaml(state[AgentRoute.TaskifierAgent], indent=2)}

# Timeline Agent
{dumps_to_yaml(state[AgentRoute.TimelineAgent], indent=2)}

Assess risks and overall feasibility. You should output a JSON format"""

    def _process_result(self, state: AgentState, result: AgentDtypes.RiskAgent) -> AgentState:
        if "warn_errors" not in state:
            state["warn_errors"] = {}
        state["warn_errors"]["dealbreakers"] = result.result.dealbreakers
        state["forward"] = (
            AgentRoute.ValidatorAgent
            if result.result.feasible or not result.result.dealbreakers
            else AgentRoute.PlannerAgent
        )
        state["backward"] = AgentRoute.RiskAgent
        return state
