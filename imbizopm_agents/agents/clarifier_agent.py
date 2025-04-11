import json
from typing import Any, Dict

from langchain_core.language_models import BaseChatModel

from ..base_agent import AgentState, BaseAgent
from ..dtypes.clarifier_types import ProjectPlan
from ..prompts.clarifier_prompts import (
    get_clarifier_output_format,
    get_clarifier_prompt,
)
from .agent_routes import AgentRoute

CLASSIFIER_OUTPUT = get_clarifier_output_format()

CLASSIFIER_PROMPT = get_clarifier_prompt()


class ClarifierAgent(BaseAgent):
    """Agent that refines the idea, extracts goals, scope, and constraints."""

    def __init__(self, llm: BaseChatModel, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.ClarifierAgent,
            CLASSIFIER_PROMPT,
            CLASSIFIER_OUTPUT,
            ProjectPlan if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        """Prepare input for the agent."""
        if state.get("current") == AgentRoute.OutcomeAgent:  # From outcome agent
            return f"""
idea: {state['input']}

# Previous Outcome Agent
Refined idea: {state['idea'].get('refined', '')}
goals: {json.dumps(state.get('goals', []), indent=2)}
constraints: {json.dumps(state.get('constraints', []), indent=2)}

From the previous refined idea, goals, and constraints, it was not possible to extract clear success_metrics and deliverables. Please clarify the project idea, goals, and constraints.
"""
        elif state.get("current") == AgentRoute.PlannerAgent:  # From planner agent
            return f"""
idea: {state['input']}

# Previous Clarifier Agent
Refined idea: {state['idea'].get('refined', '')}
goals: {json.dumps(state.get('goals', []), indent=2)}
constraints: {json.dumps(state.get('constraints', []), indent=2)}

# Previous Outcome Agent
outcomes: {json.dumps(state.get('outcomes', []), indent=2)}
deliverables: {json.dumps(state.get('deliverables', []), indent=2)}

# Previous Planner Agent
phases: {json.dumps(state['plan'].get('phases', []), indent=2)}
epics: {json.dumps(state['plan'].get('epics', []), indent=2)}
strategies: {json.dumps(state['plan'].get('strategies', []), indent=2)}
vague_feedback: {json.dumps(state['plan'].get('vague_feedback', {}), indent=2)}

From the previous refined idea, goals, constraints, it was not possible to extract clear phases, epics, and strategies. Please clarify the project idea, goals, and constraints.
"""
        elif state.get("current") == AgentRoute.TaskifierAgent:
            return f"""
idea: {state['input']}

# Previous Clarifier Agent
Refined idea: {state['idea'].get('refined', '')}
goals: {json.dumps(state.get('goals', []), indent=2)}
constraints: {json.dumps(state.get('constraints', []), indent=2)}

# Previous Outcome Agent
outcomes: {json.dumps(state.get('outcomes', []), indent=2)}
deliverables: {json.dumps(state.get('deliverables', []), indent=2)}

# Previous Planner Agent
phases: {json.dumps(state['plan'].get('phases', []), indent=2)}
epics: {json.dumps(state['plan'].get('epics', []), indent=2)}
strategies: {json.dumps(state['plan'].get('strategies', []), indent=2)}
vague_feedback: {json.dumps(state['plan'].get('vague_feedback', {}), indent=2)}

# Taskifier Agent
Missing info: {json.dumps(state['warn_errors'].get('missing_info', {}), indent=2)}

From the previous refined idea, goals, constraints, it was not possible to extract clear tasks. Please clarify the project idea, goals, and constraints.
"""
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
                prompt_parts.append(
                    f"Taskifier feedback: {json.dumps(missing_info, indent=2)}"
                )

        # Check for PlannerAgent feedback
        if state.get("plan") and state["plan"] and state["plan"].get("vague_feedback"):
            prompt_parts.append(
                f"Planner feedback: {json.dumps(state['plan'].get('vague_feedback'), indent=2)}"
            )

        return "\n".join(prompt_parts)

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["idea"] = {"refined": result.get("refined_idea", "")}
        state["goals"] = result.get("goals", [])
        state["constraints"] = result.get("constraints", [])
        state["next"] = AgentRoute.OutcomeAgent
        state["current"] = AgentRoute.ClarifierAgent
        return state
