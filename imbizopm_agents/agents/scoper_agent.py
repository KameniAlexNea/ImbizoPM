from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..prompts import SCOPER_PROMPT
from .agent_routes import AgentRoute
from .utils import format_list

class ScoperAgent(BaseAgent):
    """Agent that trims the plan into an MVP and resolves overload."""

    def __init__(self, llm):
        super().__init__(llm, "Scoper", SCOPER_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        prompt_parts = []

        if state["plan"].get("phases"):
            prompt_parts.append(f"Phases: {state['plan'].get('phases', [])}")

        if state["plan"].get("epics"):
            prompt_parts.append(f"Epics: {state['plan'].get('epics', [])}")

        if state.get("constraints"):
            prompt_parts.append(
                f"Constraints:\n{format_list(state.get('constraints', []))}"
            )

        # Check for negotiation details from NegotiatorAgent
        if state.get("scope") and state["scope"].get("negotiation_details"):
            prompt_parts.append(
                f"Negotiation details:\n{state['scope'].get('negotiation_details')}"
            )

        prompt_parts.append("Define MVP scope and resolve overload.")

        return "\n".join(prompt_parts)

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["scope"] = {
            "mvp": result.get("mvp_scope", {}),
            "exclusions": result.get("scope_exclusions", []),
            "phased_approach": result.get("phased_approach", []),
        }
        state["next"] = (
            AgentRoute.NegotiatorAgent if result.get("overload", False) else AgentRoute.TaskifierAgent
        )
        return state
