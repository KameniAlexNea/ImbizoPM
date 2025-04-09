from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute

TASKIFIER_PROMPT = """You are the Taskifier Agent. Your job is to break down the plan into detailed, actionable tasks with clear ownership and dependencies.

PROCESS:
1. Review the project plan, phases, and epics
2. Break each epic down into specific, discrete tasks
3. Identify dependencies between tasks
4. Assign appropriate owner roles for each task
5. Estimate relative effort for each task
6. Check if sufficient information exists to create meaningful tasks

GUIDELINES:
- Each task should be small enough to be completed by one person in 1-3 days
- Task descriptions should clearly describe what needs to be done
- Dependencies should form a logical sequence of work
- Effort estimates should consider complexity, not just time
- Owner roles should match the skills required for the task
- Identify any areas where more information is needed before tasks can be defined

OUTPUT FORMAT:
{{
  "tasks": [
    {{
		"id": "T1",
		"name": "Descriptive task name",
		"description": "Detailed description of what needs to be done",
		"deliverable": "Which deliverable this task contributes to",
		"owner_role": "Role responsible for completing this task",
		"dependencies": ["T2", "T3"],
		"estimated_effort": "Low/Medium/High",
		"epic": "Parent epic name",
		"phase": "Phase where this task should be completed"
	}},
    ...
  ],
  "missing_info": false,
  "missing_info_details": {{}}
}}

If information is missing:
{{
    "missing_info": true,
    "missing_info_details": {{
        "unclear_aspects": [
            "Specific aspect that prevents task definition",
            "..."
        ],
        "questions": [
            "Specific question that needs answering before tasks can be defined",
            "..."
        ],
        "suggestions": [
            "Concrete suggestion to address the lack of clarity",
            "..."
        ]
    }},
    "tasks": []
}}"""


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
            AgentRoute.ClarifierAgent
            if result.get("missing_info", False)
            else AgentRoute.TimelineAgent
        )
        return state
