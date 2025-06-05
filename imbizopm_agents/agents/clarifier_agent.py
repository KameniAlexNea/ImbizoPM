from langchain_core.language_models import BaseChatModel

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import ProjectPlan
from ..prompts.clarifier_prompts import (
    get_clarifier_output_format,
    get_clarifier_prompt,
)
from .base_agent import AgentState, BaseAgent
from .config import AgentDtypes, AgentRoute


class ClarifierAgent(BaseAgent):
    """Agent that refines the idea, extracts goals, scope, and constraints."""

    def __init__(
        self,
        llm: BaseChatModel,
        use_structured_output: bool = False,
        use_two_step_generation: bool = True,
    ):
        model_cls = ProjectPlan if use_structured_output else None
        super().__init__(
            llm,
            name=AgentRoute.ClarifierAgent,
            format_prompt=get_clarifier_output_format(),
            system_prompt=get_clarifier_prompt(),
            model_class=model_cls if not use_two_step_generation else ProjectPlan,
            prepare_input=self._prepare_input_logic,
            process_result=self._process_result_logic,
            next_step=self._next_step_logic,
            use_two_step_generation=use_two_step_generation,
        )

    def _prepare_input_logic(self, state: AgentState) -> str:
        """Prepares the input prompt based on the current state, potentially incorporating feedback."""
        backward_route = state.get("backward")  # Get the string directly

        # Check if backward route is PlannerAgent string
        if backward_route == AgentRoute.PlannerAgent:
            planner_state = state.get(AgentRoute.PlannerAgent)
            vague_details = getattr(
                planner_state, "vague_details", "No details provided"
            )
            return f"""
idea: {state['input']}

# Previous Clarifier Agent Output:
{dumps_to_yaml(state.get(AgentRoute.ClarifierAgent))}

# Feedback from Planner Agent (Vague Details):
{dumps_to_yaml(vague_details)}

The previous plan generation failed due to unclear aspects. Please refine the project idea, goals, and constraints based on the feedback provided to ensure clear phases, epics, and strategies can be derived.
"""
        # Check if backward route is TaskifierAgent string
        elif backward_route == AgentRoute.TaskifierAgent:
            taskifier_state = state.get(AgentRoute.TaskifierAgent)
            missing_info = getattr(
                taskifier_state, "missing_info_details", "No details provided"
            )
            planner_components = getattr(
                state.get(AgentRoute.PlannerAgent), "components", {}
            )
            return f"""
idea: {state['input']}

# Previous Clarifier Agent Output:
{dumps_to_yaml(state.get(AgentRoute.ClarifierAgent))}

# Current Plan Components:
{dumps_to_yaml(planner_components)}

# Feedback from Taskifier Agent (Missing Information):
{dumps_to_yaml(missing_info)}

Generating detailed tasks failed because some information was missing or unclear. Please refine the project idea, goals, and constraints based on the feedback to enable task breakdown.
"""
        # Default: Initial input or coming from a non-feedback route
        return state["input"]

    def _process_result_logic(
        self, state: AgentState, result: AgentDtypes.ClarifierAgent
    ) -> AgentState:
        """Processes the result, setting the backward route."""
        state["backward"] = AgentRoute.ClarifierAgent  # Store string
        return state

    def _next_step_logic(
        self, state: AgentState, result: AgentDtypes.ClarifierAgent
    ) -> AgentRoute:
        """Determines the next agent to route to."""
        return AgentRoute.PlannerAgent
