import json
from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..dtypes.scoper_types import ScopeDefinition
from ..prompts.scoper_prompts import (
    get_scoper_output_format,
    get_scoper_prompt,
)
from ..agent_routes import AgentRoute
from .utils import format_list

SCOPER_OUTPUT = get_scoper_output_format()

SCOPER_PROMPT = get_scoper_prompt()


class ScoperAgent(BaseAgent):
    """Agent that trims the plan into an MVP and resolves overload."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.ScoperAgent,
            SCOPER_PROMPT,
            SCOPER_OUTPUT,
            ScopeDefinition if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        prompt_parts = [f"Refined idea:\n {state['idea'].get('refined', '')}"]

        if state["plan"].get("phases"):
            prompt_parts.append(
                f"Phases: {json.dumps(state['plan'].get('phases', []), indent=2)}"
            )

        if state["plan"].get("epics"):
            prompt_parts.append(
                f"Epics: {json.dumps(state['plan'].get('epics', []), indent=2)}"
            )

        if state.get("constraints"):
            prompt_parts.append(
                f"Constraints:\n{format_list(state.get('constraints', []))}"
            )

        # Check for negotiation details from NegotiatorAgent
        if state.get("warn_errors") and state["warn_errors"].get("negotiation_details"):
            prompt_parts.append(
                f"Negotiation details:\n{state['warn_errors'].get('negotiation_details')}"
            )
            state["warn_errors"].pop("negotiation_details")

        prompt_parts.append("Define MVP scope and resolve overload.")

        return "\n".join(prompt_parts)

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["scope"] = {
            "mvp": result.get("mvp_scope", {}),
            "exclusions": result.get("scope_exclusions", []),
            "phased_approach": result.get("phased_approach", []),
        }
        if result.get("overload", False):
            state["scope"]["overload"] = result.get("overload_details", {})
        state["next"] = (
            AgentRoute.NegotiatorAgent
            if result.get("overload", False) and result.get("overload_details", {})
            else AgentRoute.TaskifierAgent
        )
        state["current"] = AgentRoute.ScoperAgent
        return state
