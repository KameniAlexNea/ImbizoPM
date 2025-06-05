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

    def __init__(
        self,
        llm,
        use_structured_output: bool = False,
        use_two_step_generation: bool = True,
    ):
        model_cls = PlanValidation if use_structured_output else None
        super().__init__(
            llm,
            name=AgentRoute.ValidatorAgent,
            # Correct order: system_prompt first, then format_prompt
            system_prompt=get_validator_prompt(),
            format_prompt=get_validator_output_format(),
            model_class=model_cls if not use_two_step_generation else PlanValidation,
            prepare_input=self._prepare_input_logic,
            process_result=self._process_result_logic,
            next_step=self._next_step_logic,
            use_two_step_generation=use_two_step_generation,
        )

    def _prepare_input_logic(self, state: AgentState) -> str:
        """Prepares the input prompt using the clarified idea, plan, and tasks."""
        clarifier_output = state.get(AgentRoute.ClarifierAgent, {})
        planner_output = state.get(AgentRoute.PlannerAgent)  # Or Scoper if used
        taskifier_output = state.get(AgentRoute.TaskifierAgent)
        # Optionally include Risk assessment summary
        risk_output = state.get(AgentRoute.RiskAgent)
        risk_summary = {
            "feasible": getattr(risk_output, "feasible", "N/A"),
            "key_risks": getattr(risk_output, "key_risks", []),
        }

        plan_components = getattr(planner_output, "components", {})
        tasks = getattr(taskifier_output, "tasks", [])

        return f"""# Clarified Project Goals & Constraints:
{dumps_to_yaml(clarifier_output, indent=4)}

# Plan Components:
{dumps_to_yaml(plan_components, indent=4)}

# Detailed Tasks:
{dumps_to_yaml(tasks, indent=4)}

# Risk Assessment Summary:
{dumps_to_yaml(risk_summary, indent=4)}

Validate the overall alignment and completeness of the project plan. Check if the plan components and tasks effectively address the clarified goals and respect the constraints. Verify if the identified risks have been adequately considered or mitigated in the plan/tasks. Output should be in JSON format, indicating validity and any gaps or misalignments found.
"""

    def _process_result_logic(
        self, state: AgentState, result: AgentDtypes.ValidatorAgent
    ) -> AgentState:
        """Processes the result, setting the backward route."""
        state["backward"] = AgentRoute.ValidatorAgent  # Store string
        return state

    def _next_step_logic(
        self, state: AgentState, result: AgentDtypes.ValidatorAgent
    ) -> AgentRoute:
        """Determines the next agent based on validation success."""
        # If valid, proceed to PMAdapter
        if result.is_valid():
            return AgentRoute.PMAdapterAgent
        # Otherwise (invalid), go back to Planner to fix issues
        else:
            return AgentRoute.PlannerAgent
