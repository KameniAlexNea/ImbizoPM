from typing import Union  # Add Union

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import ConflictResolution
from ..prompts.negotiator_prompts import (
    get_negotiator_output_format,
    get_negotiator_prompt,
)
from .base_agent import AgentState, BaseAgent
from .config import AgentDtypes, AgentRoute


class NegotiatorAgent(BaseAgent):
    """Agent that coordinates conflict resolution among agents."""

    def __init__(
        self,
        llm,
        use_structured_output: bool = False,
        use_two_step_generation: bool = True,
    ):
        model_cls = ConflictResolution if use_structured_output else None
        super().__init__(
            llm,
            name=AgentRoute.NegotiatorAgent,
            format_prompt=get_negotiator_output_format(),
            system_prompt=get_negotiator_prompt(),
            model_class=(
                model_cls if not use_two_step_generation else ConflictResolution
            ),
            prepare_input=self._prepare_input_logic,
            process_result=self._process_result_logic,
            next_step=self._next_step_logic,
            use_two_step_generation=use_two_step_generation,
        )

    def _prepare_input_logic(self, state: AgentState) -> str:
        """Prepares the input prompt using the idea, scope, and plan components."""
        clarifier_output = state.get(AgentRoute.ClarifierAgent)
        refined_idea = getattr(clarifier_output, "refined_idea", "N/A")

        scoper_output = state.get(
            AgentRoute.ScoperAgent
        )  # Output from Scoper (where overload was detected)
        planner_output = state.get(AgentRoute.PlannerAgent)
        planner_components = getattr(planner_output, "components", {})

        # It's crucial to include the specific overload details from Scoper
        overload_details = getattr(
            getattr(scoper_output, "overload", None),
            "problem_areas",
            "Overload detected, specific areas not detailed.",
        )

        return f"""# Project Idea:
{refined_idea}

# Current Plan Components:
{dumps_to_yaml(planner_components)}

# Scope Definition (Causing Conflict):
{dumps_to_yaml(scoper_output)}

# Identified Overload / Conflict Areas:
{dumps_to_yaml(overload_details)}

A conflict or overload has been identified, primarily related to the scope definition. Analyze the conflict between the project idea, the plan components, and the defined scope (especially the overload areas). Propose negotiation points or adjustments primarily to the scope, but potentially also to the plan, to resolve the conflict.
"""

    def _process_result_logic(
        self, state: AgentState, result: AgentDtypes.NegotiatorAgent
    ) -> AgentState:
        """Processes the result, setting the backward route."""
        state["backward"] = AgentRoute.NegotiatorAgent  # Store string
        return state

    def _next_step_logic(
        self, state: AgentState, result: AgentDtypes.NegotiatorAgent
    ) -> AgentRoute:
        """Determines the next agent based on the type of conflict identified."""
        # Routes back to the agent responsible for the conflict area for revision
        # Based on the prompt, conflict is usually scope vs plan/idea
        if (
            result.is_scope_conflict()
        ):  # Check if the resolution primarily impacts scope
            return (
                AgentRoute.ScoperAgent
            )  # Send back to Scoper with negotiation suggestions
        else:
            # If negotiation suggests plan changes are needed more than scope
            return AgentRoute.PlannerAgent  # Send back to Planner
