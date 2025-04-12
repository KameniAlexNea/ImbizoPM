import json

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..base_agent import AgentState, BaseAgent
from ..dtypes.planner_types import ProjectPlanOutput
from ..prompts.planner_prompts import (
    get_planner_output_format,
    get_planner_prompt,
)
from .config import AgentDtypes, AgentRoute


class PlannerAgent(BaseAgent):
    """Agent that breaks the project into phases, epics, and strategies."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.PlannerAgent,
            get_planner_output_format(),
            get_planner_prompt(),
            ProjectPlanOutput if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        prompt_parts = [
            f"""# Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent], indent=2)}

# Outcome Agent
{dumps_to_yaml(state[AgentRoute.OutcomeAgent], indent=2)}
"""
        ]
        # Check for negotiation details from NegotiatorAgent
        flag = False
        if state.get("warn_errors") and state["warn_errors"].get("negotiation_details"):
            prompt_parts.append(f"Some issues were raised during negotiation.")
            prompt_parts.append(
                f"Negotiation details:\n{json.dumps(state['warn_errors'].get('negotiation_details'), indent=2)}"
            )
            state["warn_errors"].pop("negotiation_details")
            flag = True

        # Check for risk details from RiskAgent
        if state.get("warn_errors") and state["warn_errors"].get("dealbreakers"):
            prompt_parts.append(f"Some issues were raised during risk assessment.")
            prompt_parts.append(
                f"Risks details:\n{json.dumps(state['warn_errors'].get('dealbreakers'), indent=2)}"
            )
            state["warn_errors"].pop("dealbreakers")
            flag = True

        # Check for validation details from ValidatorAgent
        if state.get("forward") == AgentRoute.ValidatorAgent:
            prompt_parts.append(f"Some issues were raised during validation.")
            prompt_parts.append(
                f"Validation details:\n{json.dumps(state['validation'], indent=2)}"
            )
            state["validation"] = dict()
            flag = True

        if flag:
            prompt_parts.append(
                f"Previous plan with issue:\n{dumps_to_yaml(state[AgentRoute.PlannerAgent], indent=2)}"
            )

        prompt_parts.append("Break into phases, epics, and strategies.")

        return "\n".join(prompt_parts)

    def _process_result(
        self, state: AgentState, result: AgentDtypes.PlannerAgent
    ) -> AgentState:
        state["forward"] = (
            AgentRoute.ClarifierAgent
            if result.too_vague and result.vague_details.unclear_aspects
            else (
                AgentRoute.ScoperAgent
                if state["backward"] != AgentRoute.NegotiatorAgent
                else AgentRoute.NegotiatorAgent
            )
        )
        state["backward"] = AgentRoute.PlannerAgent
        return state
