from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..prompts import OUTCOME_PROMPT
from .agent_routes import AgentRoute
from .utils import format_list

class OutcomeAgent(BaseAgent):
    """Agent that defines success metrics and deliverables."""

    def __init__(self, llm):
        super().__init__(llm, "Outcome", OUTCOME_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""Refined idea:
{state['idea'].get('refined', '')}
Goals:
{format_list(state.get('goals', []))}
Constraints:
{format_list(state.get('constraints', []))}

Define success metrics and deliverables."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["outcomes"] = result.get("success_metrics", [])
        state["deliverables"] = result.get("deliverables", [])
        state["next"] = AgentRoute.PlannerAgent if state["outcomes"] else AgentRoute.ClarifierAgent
        return state
