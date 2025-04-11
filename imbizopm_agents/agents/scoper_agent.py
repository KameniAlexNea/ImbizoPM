from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..agent_routes import AgentDtypes, AgentRoute
from ..base_agent import AgentState, BaseAgent
from ..dtypes.scoper_types import ScopeDefinition
from ..prompts.scoper_prompts import (
    get_scoper_output_format,
    get_scoper_prompt,
)


class ScoperAgent(BaseAgent):
    """Agent that trims the plan into an MVP and resolves overload."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.ScoperAgent,
            get_scoper_output_format(),
            get_scoper_prompt(),
            ScopeDefinition if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        prompt_parts = [
            f"""# Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent], indent=2)}

# Planner Agent
{dumps_to_yaml(state[AgentRoute.PlannerAgent], indent=2)}
"""
        ]

        # Check for negotiation details from NegotiatorAgent
        if state.get("warn_errors") and state["warn_errors"].get("negotiation_details"):
            prompt_parts.append(
                f"Negotiation details:\n{dumps_to_yaml(state['warn_errors'].get('negotiation_details'))}"
            )

            prompt_parts.append(
                f"Previous Scope Agent:\n{dumps_to_yaml(state[AgentRoute.ScoperAgent])}"
            )
            state["warn_errors"].pop("negotiation_details")

        prompt_parts.append("Define MVP scope and resolve overload.")

        return "\n".join(prompt_parts)

    def _process_result(
        self, state: AgentState, result: AgentDtypes.ScoperAgent
    ) -> AgentState:
        if result.result.overload:
            state["scope"]["overload"] = result.result.overload_details
        state["forward"] = (
            AgentRoute.NegotiatorAgent
            if result.result.overload and result.result.overload_details
            else AgentRoute.TaskifierAgent
        )
        state["backward"] = AgentRoute.ScoperAgent
        return state
