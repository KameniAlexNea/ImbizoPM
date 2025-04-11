import json
from typing import Any, Dict

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..base_agent import AgentState, BaseAgent
from ..dtypes.taskifier_types import TaskPlan
from ..prompts.taskifier_prompts import (
    get_taskifier_output_format,
    get_taskifier_prompt,
)
from ..agent_routes import AgentDtypes, AgentRoute

class TaskifierAgent(BaseAgent):
    """Agent that produces detailed tasks with owners and dependencies."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.TaskifierAgent,
            get_taskifier_output_format(),
            get_taskifier_prompt(),
            TaskPlan if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""# Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent], indent=2)}

# Scoper Agent
{dumps_to_yaml(state[AgentRoute.ScoperAgent], indent=2)}

# Planner Agent
{dumps_to_yaml(state[AgentRoute.PlannerAgent], indent=2)}

Break into detailed tasks with effort, roles, and dependencies."""

    def _process_result(self, state: AgentState, result: AgentDtypes.TaskifierAgent) -> AgentState:
        tasks = result.result.tasks

        # If missing info, store feedback in the tasks structure
        if result.result.missing_info and result.result.missing_info_details:
            # Create a special task to carry the feedback
            if "warn_errors" not in state:
                state["warn_errors"] = {}
            state["warn_errors"]["missing_info"] = result.result.missing_info_details

        state["forward"] = (
            AgentRoute.ClarifierAgent
            if result.result.missing_info or not tasks
            else AgentRoute.TimelineAgent
        )
        state["backward"] = AgentRoute.TaskifierAgent
        return state
