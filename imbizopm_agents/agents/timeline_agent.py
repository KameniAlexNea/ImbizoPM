from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute

TIMELINE_PROMPT = """You are the Timeline Agent. Your job is to create a realistic project timeline with task durations, dependencies, and key milestones.

PROCESS:
1. Review all tasks and their dependencies
2. Assign realistic durations to each task
3. Calculate start and end dates based on dependencies
4. Identify key milestones that mark significant progress
5. Determine the critical path of tasks that directly impact the project duration
6. Account for parallel work where possible to optimize the timeline

GUIDELINES:
- Use T+X format where T is project start and X is days/weeks from start
- Account for dependencies when calculating start dates
- Include buffer time for high-risk or complex tasks
- Ensure milestones represent meaningful completion points
- The critical path should identify tasks where delays directly impact the project end date
- Consider resource constraints when scheduling parallel tasks

OUTPUT FORMAT:
{{
    "task_durations": {{
        "T1": {{"start": "T+0", "end": "T+2"}},
        "T2": {{"start": "T+2", "end": "T+4"}},
        ...
    }},
    "milestones": ["M1: Repo Initialized", "M2: MVP Complete"],
    "critical_path": ["T1", "T5", "T7", "..."]
}}"""


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
