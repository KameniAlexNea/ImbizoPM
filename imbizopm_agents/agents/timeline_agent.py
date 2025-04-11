import json
from typing import Any, Dict

from imbizopm_agents.prompts.timeline_prompts import (
    get_timeline_output_format,
    get_timeline_prompt,
)

from ..base_agent import AgentState, BaseAgent
from ..dtypes.timeline_types import ProjectTimeline
from ..agent_routes import AgentRoute

TIMELINE_OUTPUT = get_timeline_output_format()

TIMELINE_PROMPT = get_timeline_prompt()


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
