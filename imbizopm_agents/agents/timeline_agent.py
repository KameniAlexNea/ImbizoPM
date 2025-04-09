from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..prompts import TIMELINE_PROMPT
from .agent_routes import AgentRoute

class TimelineAgent(BaseAgent):
    """Agent that maps tasks to durations and milestones."""

    def __init__(self, llm):
        super().__init__(llm, "Timeline", TIMELINE_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""Tasks:
{state.get("tasks", [])}

Estimate timeline with milestones and critical path."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["timeline"] = {
            "task_durations": result.get("task_durations", {}),
            "milestones": result.get("milestones", []),
            "critical_path": result.get("critical_path", []),
        }
        state["next"] = AgentRoute.RiskAgent
        return state
