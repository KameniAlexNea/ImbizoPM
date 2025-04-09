from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..prompts import RISK_PROMPT
from .agent_routes import AgentRoute

class RiskAgent(BaseAgent):
    """Agent that reviews feasibility and spots contradictions."""

    def __init__(self, llm):
        super().__init__(llm, "Risk", RISK_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""Plan: {state.get("plan", {})}
Scope: {state.get("scope", {})}
Tasks: {state.get("tasks", [])}
Timeline: {state.get("timeline", {})}

Assess risks and overall feasibility."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["risks"] = result.get("risks", [])
        state["feasibility"] = result.get("feasible", True)
        state["next"] = (
            AgentRoute.ValidatorAgent if result.get("feasible", True) else AgentRoute.PlannerAgent
        )
        return state
