from typing import Union  # Add Union
from imbizopm_agents.prompts.timeline_prompts import (
    get_timeline_output_format,
    get_timeline_prompt,
)
from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import ProjectTimeline
from .base_agent import AgentState, BaseAgent, END  # Import END if needed
from .config import AgentDtypes, AgentRoute


class TimelineAgent(BaseAgent):
    """Agent that maps tasks to durations and milestones."""

    def __init__(self, llm, use_structured_output: bool = False):
        model_cls = ProjectTimeline if use_structured_output else None
        super().__init__(
            llm,
            name=AgentRoute.TimelineAgent,
            format_prompt=get_timeline_output_format(),
            system_prompt=get_timeline_prompt(),
            model_class=model_cls,
            prepare_input=self._prepare_input_logic,
            process_result=self._process_result_logic,
            next_step=self._next_step_logic,
        )

    def _prepare_input_logic(self, state: AgentState) -> str:
        """Prepares the input prompt using the clarified idea and task list."""
        clarifier_output = state.get(AgentRoute.ClarifierAgent, {})
        taskifier_output = state.get(AgentRoute.TaskifierAgent)
        tasks = getattr(taskifier_output, 'tasks', [])

        # Consider including constraints from Clarifier if relevant to timeline
        constraints = getattr(clarifier_output, 'constraints', [])

        return f"""# Clarified Project Details (Constraints):
{dumps_to_yaml(constraints, indent=4)}

# Detailed Tasks:
{dumps_to_yaml(tasks, indent=4)}

Estimate the duration for each task. Sequence the tasks considering their dependencies and estimate an overall project timeline. Identify key milestones and the critical path. Highlight any potential timeline risks based on the tasks and constraints.
"""

    def _process_result_logic(
        self, state: AgentState, result: AgentDtypes.TimelineAgent
    ) -> AgentState:
        """Processes the result, setting the backward route."""
        state["backward"] = AgentRoute.TimelineAgent  # Store string
        return state

    def _next_step_logic(self, state: AgentState, result: AgentDtypes.TimelineAgent) -> AgentRoute:
        """Determines the next agent to route to."""
        return AgentRoute.RiskAgent
