from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..prompts import VALIDATOR_PROMPT
from .agent_routes import AgentRoute

class ValidatorAgent(BaseAgent):
    """Agent that verifies alignment between idea, plan, and goals."""

    def __init__(self, llm):
        super().__init__(llm, "Validator", VALIDATOR_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""
Original idea: {state['idea'].get('refined', '')}
Goals: {', '.join(state['goals'])}
Constraints: {', '.join(state['constraints'])}
Outcomes: {', '.join(state['outcomes'])}
Plan: {state['plan']}
Scope: {state['scope']}
Tasks: {state['tasks']}

Validate alignment between the idea, goals, and the resulting plan."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["validation"] = {
            "goals_alignment": result.get("goals_alignment", {}),
            "constraints_respected": result.get("constraints_respected", {}),
            "outcomes_achievable": result.get("outcomes_achievable", {}),
            "overall": result.get("overall_validation", False),
        }

        # Check validation result
        state["next"] = AgentRoute.PMAdapterAgent if state["validation"]["overall"] else AgentRoute.PlannerAgent
        return state
