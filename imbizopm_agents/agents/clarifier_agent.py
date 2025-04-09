from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..prompts import CLASSIFIER_PROMPT
from .agent_routes import AgentRoute

class ClarifierAgent(BaseAgent):
    """Agent that refines the idea, extracts goals, scope, and constraints."""

    def __init__(self, llm):
        super().__init__(llm, "Clarifier", CLASSIFIER_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        """Prepare input for the agent."""
        prompt_parts = [state["input"]]

        # Check for TaskifierAgent feedback
        if (
            state.get("tasks")
            and state["tasks"]
            and isinstance(state["tasks"], list)
            and len(state["tasks"]) > 0
        ):
            if any(task.get("missing_info_feedback") for task in state["tasks"]):
                missing_info = [
                    task.get("missing_info_feedback")
                    for task in state["tasks"]
                    if task.get("missing_info_feedback")
                ]
                prompt_parts.append(f"Taskifier feedback: {missing_info}")

        # Check for PlannerAgent feedback
        if state.get("plan") and state["plan"] and state["plan"].get("vague_feedback"):
            prompt_parts.append(
                f"Planner feedback: {state['plan'].get('vague_feedback')}"
            )

        return "\n".join(prompt_parts)

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["idea"] = {"refined": result.get("refined_idea", "")}
        state["goals"] = result.get("goals", [])
        state["constraints"] = result.get("constraints", [])
        state["next"] = AgentRoute.OutcomeAgent
        return state
