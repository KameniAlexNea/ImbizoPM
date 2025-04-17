from typing import Any, Dict

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import ProjectSummary
from ..prompts.pm_adapter_prompts import (
    get_pm_adapter_output_format,
    get_pm_adapter_prompt,
)
from .base_agent import AgentState, BaseAgent
from .config import AgentRoute


class PMAdapterAgent(BaseAgent):
    """Agent that formats and exports the project plan for external tools."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.PMAdapterAgent,
            get_pm_adapter_output_format(),
            get_pm_adapter_prompt(),
            ProjectSummary if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f""""# Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent], indent=4)}

# Project Plan:
{dumps_to_yaml(state[AgentRoute.PlannerAgent].components, indent=4)}

# Project Tasks:
{dumps_to_yaml(state[AgentRoute.TaskifierAgent].tasks, indent=4)}

# Project Timeline:
{dumps_to_yaml(state[AgentRoute.TimelineAgent], indent=4)}

# Project Risks:
{dumps_to_yaml(state[AgentRoute.RiskAgent], indent=4)}

# Validation:
{dumps_to_yaml(state[AgentRoute.ValidatorAgent], indent=4)}

Format this project plan for exporting to JSON. Stricly output only the JSON, to the appropriate format."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        # This is the final agent, no next state needed
        state["forward"] = AgentRoute.END
        state["backward"] = AgentRoute.PMAdapterAgent
        return state
