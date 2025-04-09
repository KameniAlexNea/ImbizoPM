from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..prompts import PLANNER_PROMPT
from .agent_routes import AgentRoute
from .utils import format_list

class PlannerAgent(BaseAgent):
    """Agent that breaks the project into phases, epics, and strategies."""

    def __init__(self, llm):
        super().__init__(llm, "Planner", PLANNER_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        prompt_parts = [f"Refined idea: {state['idea'].get('refined', '')}"]

        if state.get("goals"):
            prompt_parts.append(f"Goals:\n{format_list(state.get('goals', []))}")

        if state.get("constraints"):
            prompt_parts.append(
                f"Constraints:\n{format_list(state.get('constraints', []))}"
            )

        if state.get("outcomes"):
            prompt_parts.append(f"Outcomes:\n{format_list(state.get('outcomes', []))}")

        deliverables = [d.get("name", "") for d in state.get("deliverables", [])]
        if deliverables:
            prompt_parts.append(f"Deliverables:\n{format_list(deliverables)}")

        # Check for negotiation details from NegotiatorAgent
        if state.get("scope") and state["scope"].get("negotiation_details"):
            prompt_parts.append(
                f"Negotiation details:\n{state['scope'].get('negotiation_details')}"
            )

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
            AgentRoute.ClarifierAgent if result.get("too_vague", False) else AgentRoute.ScoperAgent
        )
        return state
