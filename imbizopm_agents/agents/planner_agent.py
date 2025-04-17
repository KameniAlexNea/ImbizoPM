from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import ProjectPlanOutput
from ..prompts.planner_prompts import (
    get_planner_output_format,
    get_planner_prompt,
)
from .base_agent import AgentState, BaseAgent
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
{dumps_to_yaml(state[AgentRoute.ClarifierAgent], indent=4)}
"""
        ]
        # Check for negotiation details from NegotiatorAgent
        flag = False
        if state.get("backward") == AgentRoute.NegotiatorAgent:
            prompt_parts.append(f"Some issues were raised during negotiation.")
            prompt_parts.append(
                f"Negotiation details:\n{dumps_to_yaml(state[AgentRoute.NegotiatorAgent].negotiation, indent=4)}"
            )
            flag = True

        # Check for risk details from RiskAgent
        if state.get("backward") == AgentRoute.RiskAgent:
            prompt_parts.append(f"Some dealbreaks were raised during risk assessment.")
            prompt_parts.append(
                f"Risks details:\n{dumps_to_yaml(state[AgentRoute.RiskAgent].dealbreakers, indent=4)}"
            )
            flag = True

        # Check for validation details from ValidatorAgent
        if state.get("backward") == AgentRoute.ValidatorAgent:
            prompt_parts.append(f"Some issues were raised during validation.")
            prompt_parts.append(
                f"Validation details:\n{dumps_to_yaml(state[AgentRoute.ValidatorAgent].completeness_assessment, indent=4)}"
            )
            flag = True

        if flag:
            prompt_parts.append(
                f"Previous plan with issue:\n{dumps_to_yaml(state[AgentRoute.PlannerAgent].components, indent=4)}"
            )

        prompt_parts.append("Break into phases, epics, and strategies.")

        return "\n".join(prompt_parts)

    def _process_result(
        self, state: AgentState, result: AgentDtypes.PlannerAgent
    ) -> AgentState:
        state["forward"] = (
            AgentRoute.ClarifierAgent
            if result.is_valid()
            else (
                AgentRoute.ScoperAgent
                if state["backward"] != AgentRoute.NegotiatorAgent
                else AgentRoute.NegotiatorAgent
            )
        )
        state["backward"] = AgentRoute.PlannerAgent
        return state
