import json
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute


class TaskDuration(BaseModel):
    start: str  # e.g., "T+0"
    end: str  # e.g., "T+2"


class ProjectTimeline(BaseModel):
    task_durations: Dict[str, TaskDuration] = Field(
        default_factory=dict
    )  # key: task ID
    milestones: List[str] = Field(
        default_factory=list
    )  # e.g., ["M1: Repo Initialized"]
    critical_path: List[str] = Field(default_factory=list)  # e.g., ["T1", "T5", "T7"]


TIMELINE_OUTPUT = """OUTPUT FORMAT:
{{
    "task_durations": {{
        "T1": {{"start": "T+0", "end": "T+2"}},
        "T2": {{"start": "T+2", "end": "T+4"}},
        ...
    }},
    "milestones": ["M1: Repo Initialized", "M2: MVP Complete"],
    "critical_path": ["T1", "T5", "T7", "..."]
}}
"""

TIMELINE_PROMPT = f"""You are the Timeline Agent. Your job is to create a realistic project timeline with task durations, dependencies, and key milestones.

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

{TIMELINE_OUTPUT}"""


class TimelineAgent(BaseAgent):
    """Agent that maps tasks to durations and milestones."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.TimelineAgent,
            TIMELINE_PROMPT,
            TIMELINE_OUTPUT,
            ProjectTimeline if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""
Refined idea: {state.get('idea', {}).get('refined', '')}
Goals: {json.dumps(state.get('goals', []), indent=2)}
Constraints: {json.dumps(state.get('constraints', []), indent=2)}
        
Tasks:
{json.dumps(state.get("tasks", []), indent=2)}

Estimate timeline with milestones and critical path."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["timeline"] = {
            "task_durations": result.get("task_durations", {}),
            "milestones": result.get("milestones", []),
            "critical_path": result.get("critical_path", []),
        }
        state["next"] = AgentRoute.RiskAgent
        state["current"] = AgentRoute.TimelineAgent
        return state
