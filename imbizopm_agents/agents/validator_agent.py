from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import PlanValidation
from ..prompts.validator_prompts import (
    get_validator_output_format,
    get_validator_prompt,
)
from .base_agent import AgentState, BaseAgent
from .config import AgentDtypes, AgentRoute


class ValidatorAgent(BaseAgent):
    """Agent that verifies alignment between idea, plan, and goals."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.ValidatorAgent,
            get_validator_prompt(),
            get_validator_output_format(),
            PlanValidation if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""# Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent], indent=4)}

# Plan Agent
{dumps_to_yaml(state[AgentRoute.PlannerAgent].components, indent=4)}

# Taskifier Agent
{dumps_to_yaml(state[AgentRoute.TaskifierAgent].tasks, indent=4)}

Validate alignment between the idea, goals, and the resulting plan. Stricly output only the JSON, to the appropriate format."""

    def _process_result(
        self, state: AgentState, result: AgentDtypes.ValidatorAgent
    ) -> AgentState:
        # Check validation result
        state["forward"] = (
            AgentRoute.PMAdapterAgent if result.is_valid() else AgentRoute.PlannerAgent
        )
        state["backward"] = AgentRoute.ValidatorAgent
        return state
