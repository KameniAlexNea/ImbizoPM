from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..prompts import NEGOCIATOR_PROMPT
from .agent_routes import AgentRoute

class NegotiatorAgent(BaseAgent):
    """Agent that coordinates conflict resolution among agents."""

    def __init__(self, llm):
        super().__init__(llm, "Negotiator", NEGOCIATOR_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        # Identify which aspect has conflicts
        return f"""Plan: {state['plan']}
Scope: {state['scope']}
Tasks: {state['tasks']}
Risks: {state['risks']}
Overload Details: {state['overload_details']}

Resolve conflicts in the current project state."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        # Store negotiation details in scope dictionary
        if result.get("negotiation_details"):
            if "scope" not in state:
                state["scope"] = {}
            state["scope"]["negotiation_details"] = result.get("negotiation_details")

        # Based on which aspect was negotiated, return to the appropriate agent
        conflict_area = result.get("conflict_area", "")
        state["next"] = AgentRoute.ScoperAgent if conflict_area == "scope" else AgentRoute.PlannerAgent
        return state
