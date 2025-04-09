from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..prompts import TASKIFIER_PROMPT
from .agent_routes import AgentRoute

class TaskifierAgent(BaseAgent):
    """Agent that produces detailed tasks with owners and dependencies."""

    def __init__(self, llm):
        super().__init__(llm, "Taskifier", TASKIFIER_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""MVP: {state['scope'].get('mvp', {})}
Phases: {state['plan'].get('phases', [])}
Epics: {state['plan'].get('epics', [])}

Break into detailed tasks with effort, roles, and dependencies."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        tasks = result.get("tasks", [])

        # If missing info, store feedback in the tasks structure
        if result.get("missing_info", False) and result.get("missing_info_details"):
            # Create a special task to carry the feedback
            feedback_task = {
                "missing_info_feedback": result.get("missing_info_details")
            }
            tasks.append(feedback_task)

        state["tasks"] = tasks
        state["next"] = (
            AgentRoute.ClarifierAgent if result.get("missing_info", False) else AgentRoute.TimelineAgent
        )
        return state
