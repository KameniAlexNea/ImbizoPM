from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import TaskPlan
from ..prompts.taskifier_prompts import (
    get_taskifier_output_format,
    get_taskifier_prompt,
)
from .base_agent import AgentState, BaseAgent
from .config import AgentDtypes, AgentRoute


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
{dumps_to_yaml(state[AgentRoute.ClarifierAgent], indent=4)}

# Planner Agent
{dumps_to_yaml(state[AgentRoute.PlannerAgent].components, indent=4)}

Break into detailed tasks with effort, roles, and dependencies."""

    def _process_result(
        self, state: AgentState, result: AgentDtypes.TaskifierAgent
    ) -> AgentState:
        state["forward"] = (
            AgentRoute.ClarifierAgent if result.is_valid() else AgentRoute.TimelineAgent
        )
        state["backward"] = AgentRoute.TaskifierAgent
        return state
