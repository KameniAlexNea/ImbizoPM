from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute

CLASSIFIER_OUTPUT = """Your output should be structured as follows:
{{
    "refined_idea": "A clear, concise statement of what the project aims to accomplish",
    "goals": [
        "Specific, measurable goal that addresses a core need",
        "Another well-defined objective with clear success criteria",
        "..."
    ],
    "constraints": [
        "Specific limitation or boundary that must be respected",
        "Another constraint with clear parameters",
        "..."
    ]
}}"""

CLASSIFIER_PROMPT = f"""You are the Clarifier Agent. Your job is to analyze the user's project idea and transform it into structured requirements.

PROCESS:
1. Carefully read the idea to understand the core project concept
2. Identify ambiguities or missing information in the original idea
3. Extract or infer clear goals based on the user's stated or implied needs
4. Determine realistic constraints that should apply to this project
5. Refine the idea into a concise, actionable statement

GUIDELINES:
- If the idea is vague, make reasonable assumptions based on industry standards
- Focus on clarifying the "what" and "why" before the "how"
- Consider technical, resource, timeline, and budget constraints even if not explicitly mentioned
- When receiving feedback from other agents, prioritize addressing identified ambiguities

{CLASSIFIER_OUTPUT}
"""


class ClarifierAgent(BaseAgent):
    """Agent that refines the idea, extracts goals, scope, and constraints."""

    def __init__(self, llm):
        super().__init__(
            llm, AgentRoute.ClarifierAgent, CLASSIFIER_PROMPT, CLASSIFIER_OUTPUT
        )

    def _prepare_input(self, state: AgentState) -> str:
        """Prepare input for the agent."""
        if state.get("current") == AgentRoute.OutcomeAgent:  # From outcome agent
            return f"""
idea: {state['input']}

# Previous Outcome Agent
Refined idea: {state['idea'].get('refined', '')}
goals: {state.get('goals', [])}
constraints: {state.get('constraints', [])}

From the previous refined idea, goals, and constraints, it was not possible to extract clear success_metrics and deliverables. Please clarify the project idea, goals, and constraints.
"""
        elif state.get("current") == AgentRoute.PlannerAgent:  # From planner agent
            return f"""
idea: {state['input']}

# Previous Clarifier Agent
Refined idea: {state['idea'].get('refined', '')}
goals: {state.get('goals', [])}
constraints: {state.get('constraints', [])}

# Previous Outcome Agent
outcomes: {state.get('outcomes', [])}
deliverables: {state.get('deliverables', [])}

# Previous Planner Agent
phases: {state['plan'].get('phases', [])}
epics: {state['plan'].get('epics', [])}
strategies: {state['plan'].get('strategies', [])}
vague_feedback: {state['plan'].get('vague_feedback', {})}

From the previous refined idea, goals, constraints, it was not possible to extract clear phases, epics, and strategies. Please clarify the project idea, goals, and constraints.
"""
        elif state.get("current") == AgentRoute.TaskifierAgent:
            return f"""
idea: {state['input']}

# Previous Clarifier Agent
Refined idea: {state['idea'].get('refined', '')}
goals: {state.get('goals', [])}
constraints: {state.get('constraints', [])}

# Previous Outcome Agent
outcomes: {state.get('outcomes', [])}
deliverables: {state.get('deliverables', [])}

# Previous Planner Agent
phases: {state['plan'].get('phases', [])}
epics: {state['plan'].get('epics', [])}
strategies: {state['plan'].get('strategies', [])}
vague_feedback: {state['plan'].get('vague_feedback', {})}

# Taskifier Agent
Missing info: {state['warn_errors'].get('missing_info', {})}

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
        state["current"] = AgentRoute.ClarifierAgent
        return state
