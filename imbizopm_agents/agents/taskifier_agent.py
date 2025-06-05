from typing import Union  # Add Union

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

    def __init__(
        self,
        llm,
        use_structured_output: bool = False,
        use_two_step_generation: bool = True,
    ):
        model_cls = TaskPlan if use_structured_output else None
        super().__init__(
            llm,
            name=AgentRoute.TaskifierAgent,
            format_prompt=get_taskifier_output_format(),
            system_prompt=get_taskifier_prompt(),
            model_class=model_cls if not use_two_step_generation else TaskPlan,
            prepare_input=self._prepare_input_logic,
            process_result=self._process_result_logic,
            next_step=self._next_step_logic,
            use_two_step_generation=use_two_step_generation,
        )

    def _prepare_input_logic(self, state: AgentState) -> str:
        """Prepares the input prompt using the clarified idea and plan components."""
        clarifier_output = state.get(AgentRoute.ClarifierAgent, {})
        # Use Scoper output if available (MVP definition), otherwise Planner
        scope_output = state.get(AgentRoute.ScoperAgent)
        planner_output = state.get(AgentRoute.PlannerAgent)

        AgentRoute.ScoperAgent if scope_output else AgentRoute.PlannerAgent
        plan_source_name = "Scoped Plan (MVP)" if scope_output else "Initial Plan"
        plan_components = getattr(
            scope_output or planner_output, "components", {}
        )  # Get components from scope or plan

        # TODO: Refine which parts of Clarifier/Scope/Plan are most relevant for task breakdown
        return f"""# Clarified Project Details:
{dumps_to_yaml(clarifier_output, indent=4)}

# {plan_source_name} Components:
{dumps_to_yaml(plan_components, indent=4)}

Based on the project details and the current plan components, break the work down into detailed tasks. Assign effort estimates, roles/owners, and identify dependencies between tasks. If information is missing, clearly state what is needed.
"""

    def _process_result_logic(
        self, state: AgentState, result: AgentDtypes.TaskifierAgent
    ) -> AgentState:
        """Processes the result, setting the backward route."""
        state["backward"] = AgentRoute.TaskifierAgent  # Store string
        return state

    def _next_step_logic(
        self, state: AgentState, result: AgentDtypes.TaskifierAgent
    ) -> AgentRoute:
        """Determines the next agent based on task plan validity and failure type."""
        # If tasks are valid, proceed to Timeline
        if result.is_valid():
            return AgentRoute.TimelineAgent

        # When invalid, analyze the type of failure to determine proper routing
        missing_info = getattr(result, "missing_info_details", None)

        # Check for explicit source indication in the missing info
        if missing_info and hasattr(missing_info, "source"):
            source = missing_info.source
            if source == "scope":
                return AgentRoute.ScoperAgent
            elif source == "plan":
                return AgentRoute.PlannerAgent
            elif source == "requirements":
                return AgentRoute.ClarifierAgent

        # Default to Clarifier if we can't determine the source
        return AgentRoute.ClarifierAgent
