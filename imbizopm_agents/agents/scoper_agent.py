from typing import Union  # Add Union

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import ScopeDefinition
from ..prompts.scoper_prompts import (
    get_scoper_output_format,
    get_scoper_prompt,
)
from .base_agent import AgentState, BaseAgent
from .config import AgentDtypes, AgentRoute


class ScoperAgent(BaseAgent):
    """Agent that trims the plan into an MVP and resolves overload."""

    def __init__(
        self,
        llm,
        use_structured_output: bool = False,
        use_two_step_generation: bool = True,
    ):
        model_cls = ScopeDefinition if use_structured_output else None
        super().__init__(
            llm,
            name=AgentRoute.ScoperAgent,
            format_prompt=get_scoper_output_format(),
            system_prompt=get_scoper_prompt(),
            model_class=model_cls if not use_two_step_generation else ScopeDefinition,
            prepare_input=self._prepare_input_logic,
            process_result=self._process_result_logic,
            next_step=self._next_step_logic,
            use_two_step_generation=use_two_step_generation,
        )

    def _prepare_input_logic(self, state: AgentState) -> str:
        """Prepares the input prompt, incorporating feedback from the Negotiator if necessary."""
        clarifier_output = state.get(AgentRoute.ClarifierAgent, {})
        planner_output = state.get(AgentRoute.PlannerAgent)
        planner_components = getattr(planner_output, "components", {})

        prompt_parts = [
            f"# Clarified Project Details:\n{dumps_to_yaml(clarifier_output, indent=4)}",
            f"\n# Current Plan Components:\n{dumps_to_yaml(planner_components, indent=4)}\n",
        ]

        # Check for negotiation feedback
        if state.get("backward") == AgentRoute.NegotiatorAgent:
            negotiator_output = state.get(AgentRoute.NegotiatorAgent)
            negotiation_details = getattr(
                negotiator_output, "negotiation", "No details provided"
            )
            previous_scope = state.get(
                AgentRoute.ScoperAgent
            )  # Get previous scope output

            prompt_parts.append(
                f"# Negotiation Feedback:\n{dumps_to_yaml(negotiation_details)}"
            )
            if previous_scope:
                prompt_parts.append(
                    f"\n# Previous Scope Definition (for context):\n{dumps_to_yaml(previous_scope)}"
                )
            prompt_parts.append(
                "\nPlease revise the scope based on the negotiation feedback."
            )
        else:
            prompt_parts.append(
                "Define the Minimum Viable Product (MVP) scope based on the plan. Identify potential overload."
            )

        return "\n".join(prompt_parts)

    def _process_result_logic(
        self, state: AgentState, result: AgentDtypes.ScoperAgent
    ) -> AgentState:
        """Processes the result, setting the backward route."""
        state["backward"] = AgentRoute.ScoperAgent  # Store string
        return state

    def _next_step_logic(
        self, state: AgentState, result: AgentDtypes.ScoperAgent
    ) -> AgentRoute:
        """Determines the next agent based on whether overload needs negotiation."""
        # If overload is identified, go to Negotiator
        if result.overload and result.overload.problem_areas:
            return AgentRoute.NegotiatorAgent
        # Otherwise, proceed to Taskifier
        else:
            return AgentRoute.TaskifierAgent
