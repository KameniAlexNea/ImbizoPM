import json
from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..dtypes.planner_types import ProjectPlanOutput
from ..prompts.planner_prompts import (
    get_planner_output_format,
    get_planner_prompt,
)
from .agent_routes import AgentRoute
from .utils import format_list

PLANNER_OUTPUT = get_planner_output_format()

PLANNER_PROMPT = get_planner_prompt()


class PlannerAgent(BaseAgent):
    """Agent that breaks the project into phases, epics, and strategies."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            "Planner",
            PLANNER_PROMPT,
            PLANNER_OUTPUT,
            ProjectPlanOutput if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        prompt_parts = [f"Refined idea: {state['idea'].get('refined', '')}"]
        prompt_parts.append(f"Goals:\n{format_list(state.get('goals', []))}")
        prompt_parts.append(
            f"Constraints:\n{format_list(state.get('constraints', []))}"
        )
        prompt_parts.append(f"Outcomes:\n{format_list(state.get('outcomes', []))}")
        deliverables = [d.get("name", "") for d in state.get("deliverables", [])]
        prompt_parts.append(f"Deliverables:\n{format_list(deliverables)}")

        # Check for negotiation details from NegotiatorAgent
        if state.get("warn_errors") and state["warn_errors"].get("negotiation_details"):
            prompt_parts.append(f"Some issues were raised during negotiation.")
            prompt_parts.append(
                f"Negotiation details:\n{json.dumps(state['warn_errors'].get('negotiation_details'), indent=2)}"
            )
            prompt_parts.append(
                f"Previous plan:\n{json.dumps(state['plan'], indent=2)}"
            )
            state["warn_errors"].pop("negotiation_details")

        # Check for risk details from RiskAgent
        if state.get("warn_errors") and state["warn_errors"].get("dealbreakers"):
            prompt_parts.append(f"Some issues were raised during risk assessment.")
            prompt_parts.append(
                f"Risks details:\n{json.dumps(state['warn_errors'].get('dealbreakers'), indent=2)}"
            )
            prompt_parts.append(
                f"Previous plan:\n{json.dumps(state['plan'], indent=2)}"
            )
            state["warn_errors"].pop("dealbreakers")

        # Check for validation details from ValidatorAgent
        if state.get("current") == AgentRoute.ValidatorAgent:
            prompt_parts.append(f"Some issues were raised during validation.")
            prompt_parts.append(
                f"Validation details:\n{json.dumps(state['validation'], indent=2)}"
            )
            prompt_parts.append(
                f"Previous plan:\n{json.dumps(state['plan'], indent=2)}"
            )
            state["validation"] = dict()

        prompt_parts.append("Break into phases, epics, and strategies.")

        return "\n".join(prompt_parts)

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["plan"] = {
            "phases": result.get("phases", []),
            "epics": result.get("epics", []),
            "strategies": result.get("strategies", []),
        }

        # Store feedback in plan dictionary if too vague
        if result.get("too_vague", False):
            state["plan"]["vague_feedback"] = result.get("vague_details", {})

        state["next"] = (
            AgentRoute.ClarifierAgent
            if result.get("too_vague", False) and result.get("vague_details", {})
            else (
                AgentRoute.ScoperAgent
                if state["current"] != AgentRoute.NegotiatorAgent
                else AgentRoute.NegotiatorAgent
            )
        )
        state["current"] = AgentRoute.PlannerAgent
        return state
