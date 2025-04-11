import json
from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..dtypes.negotiator_types import ConflictResolution
from ..prompts.negotiator_prompts import (
    get_negotiator_output_format,
    get_negotiator_prompt,
)
from .agent_routes import AgentRoute

NEGOCIATOR_OUTPUT = get_negotiator_output_format()

NEGOCIATOR_PROMPT = get_negotiator_prompt()


class NegotiatorAgent(BaseAgent):
    """Agent that coordinates conflict resolution among agents."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.NegotiatorAgent,
            NEGOCIATOR_PROMPT,
            NEGOCIATOR_OUTPUT,
            ConflictResolution if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        # Identify which aspect has conflicts
        return f"""Refined idea: {json.dumps(state['idea'].get('refined', ''), indent=2)}
Plan: {json.dumps(state['plan'], indent=2) if state.get('plan') else ''}
Scope: {json.dumps(state['scope'], indent=2) if state.get('scope') else ''}

Consider the plan and scope. Identify any conflicts or inconsistencies between them."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        # Store negotiation details in scope dictionary
        if result.get("negotiation_details"):
            if "warn_errors" not in state:
                state["warn_errors"] = {}
            state["warn_errors"]["negotiation_details"] = result.get(
                "negotiation_details"
            )

        # Based on which aspect was negotiated, return to the appropriate agent
        conflict_area = result.get("conflict_area", "")
        state["next"] = (
            AgentRoute.ScoperAgent
            if conflict_area == "scope"
            else AgentRoute.PlannerAgent
        )
        state["current"] = AgentRoute.NegotiatorAgent
        return state
