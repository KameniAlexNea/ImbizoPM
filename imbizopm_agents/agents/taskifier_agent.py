import json
from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..dtypes.taskifier_types import TaskPlan
from ..prompts.taskifier_prompts import (
    get_taskifier_output_format,
    get_taskifier_prompt,
)
from ..agent_routes import AgentRoute

TASKIFIER_OUTPUT = get_taskifier_output_format()

TASKIFIER_PROMPT = get_taskifier_prompt()


class TaskifierAgent(BaseAgent):
    """Agent that produces detailed tasks with owners and dependencies."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.TaskifierAgent,
            TASKIFIER_PROMPT,
            TASKIFIER_OUTPUT,
            TaskPlan if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""Refined idea: {state['idea'].get('refined', '')}
Goals and objectives: {state['goals']}
Constraints: {json.dumps(state.get('constraints', []), indent=2)}
Outcomes: {json.dumps(state.get('outcomes', []), indent=2)}

MVP: {json.dumps(state['scope'].get('mvp', {}), indent=2)}
Phases: {json.dumps(state['plan'].get('phases', []), indent=2)}
Epics: {json.dumps(state['plan'].get('epics', []), indent=2)}

Break into detailed tasks with effort, roles, and dependencies."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        tasks = result.get("tasks", [])

        # If missing info, store feedback in the tasks structure
        if result.get("missing_info", False) and result.get("missing_info_details"):
            # Create a special task to carry the feedback
            if "warn_errors" not in state:
                state["warn_errors"] = {}
            state["warn_errors"]["missing_info"] = {
                "missing_info_feedback": result.get("missing_info_details")
            }

        state["tasks"] = tasks
        state["next"] = (
            AgentRoute.ClarifierAgent
            if result.get("missing_info", False) or not tasks
            else AgentRoute.TimelineAgent
        )
        state["current"] = AgentRoute.TaskifierAgent
        return state
