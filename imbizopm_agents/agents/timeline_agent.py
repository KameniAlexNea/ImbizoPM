from imbizopm_agents.prompts.timeline_prompts import (
    get_timeline_output_format,
    get_timeline_prompt,
)
from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..base_agent import AgentState, BaseAgent
from ..dtypes.timeline_types import ProjectTimeline
from .config import AgentDtypes, AgentRoute


class TimelineAgent(BaseAgent):
    """Agent that maps tasks to durations and milestones."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.TimelineAgent,
            get_timeline_output_format(),
            get_timeline_prompt(),
            ProjectTimeline if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""# Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent], indent=2)}
        
Tasks:
{dumps_to_yaml(state[AgentRoute.TaskifierAgent].tasks, indent=2)}

Estimate timeline with milestones and critical path."""

    def _process_result(
        self, state: AgentState, result: AgentDtypes.TimelineAgent
    ) -> AgentState:
        state["forward"] = AgentRoute.RiskAgent
        state["backward"] = AgentRoute.TimelineAgent
        return state
