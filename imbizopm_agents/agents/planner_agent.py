from typing import Union  # Add Union

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import ProjectPlanOutput
from ..prompts.planner_prompts import (
    get_planner_output_format,
    get_planner_prompt,
)
from .base_agent import AgentState, BaseAgent
from .config import AgentDtypes, AgentRoute


class PlannerAgent(BaseAgent):
    """Agent that breaks the project into phases, epics, and strategies."""

    def __init__(
        self,
        llm,
        use_structured_output: bool = False,
        use_two_step_generation: bool = True,
    ):
        model_cls = ProjectPlanOutput if use_structured_output else None
        super().__init__(
            llm,
            name=AgentRoute.PlannerAgent,
            format_prompt=get_planner_output_format(),
            system_prompt=get_planner_prompt(),
            model_class=model_cls if not use_two_step_generation else ProjectPlanOutput,
            prepare_input=self._prepare_input_logic,
            process_result=self._process_result_logic,
            next_step=self._next_step_logic,
            use_two_step_generation=use_two_step_generation,
        )

    def _prepare_input_logic(self, state: AgentState) -> str:
        """Prepares the input prompt, incorporating feedback from other agents if necessary."""
        clarifier_output = state.get(AgentRoute.ClarifierAgent, {})
        prompt_parts = [
            f"# Clarified Project Details:\n{dumps_to_yaml(clarifier_output, indent=4)}\n"
        ]
        feedback_added = False
        backward_route = state.get("backward")  # Get the string directly

        # Check for feedback from specific agents
        if backward_route == AgentRoute.NegotiatorAgent:
            negotiator_output = state.get(AgentRoute.NegotiatorAgent)
            negotiation_details = getattr(
                negotiator_output, "negotiation", "No details provided"
            )
            prompt_parts.append(
                f"# Negotiation Feedback:\n{dumps_to_yaml(negotiation_details, indent=4)}"
            )
            feedback_added = True
        elif backward_route == AgentRoute.RiskAgent:
            risk_output = state.get(AgentRoute.RiskAgent)
            dealbreakers = getattr(risk_output, "dealbreakers", "No details provided")
            prompt_parts.append(
                f"# Risk Assessment Feedback (Dealbreakers):\n{dumps_to_yaml(dealbreakers, indent=4)}"
            )
            feedback_added = True
        elif backward_route == AgentRoute.ValidatorAgent:
            validator_output = state.get(AgentRoute.ValidatorAgent)
            validation_issues = getattr(
                validator_output, "completeness_assessment", "No details provided"
            )  # Assuming this holds issues
            prompt_parts.append(
                f"# Validation Feedback:\n{dumps_to_yaml(validation_issues, indent=4)}"
            )
            feedback_added = True

        # Include previous plan if there was feedback
        if feedback_added:
            previous_plan = state.get(AgentRoute.PlannerAgent)
            previous_components = getattr(previous_plan, "components", {})
            prompt_parts.append(
                f"\n# Previous Plan (for context):\n{dumps_to_yaml(previous_components, indent=4)}"
            )
            prompt_parts.append(
                "\nPlease revise the plan based on the feedback provided."
            )
        else:
            prompt_parts.append(
                "Based on the clarified details, break the project into phases, epics, and strategies."
            )

        return "\n".join(prompt_parts)

    def _process_result_logic(
        self, state: AgentState, result: AgentDtypes.PlannerAgent
    ) -> AgentState:
        """Processes the result, setting the backward route."""
        state["backward"] = AgentRoute.PlannerAgent  # Store string
        return state

    def _next_step_logic(
        self, state: AgentState, result: AgentDtypes.PlannerAgent
    ) -> AgentRoute:
        """Determines the next agent based on the plan's validity and context."""
        # If the plan is invalid (e.g., missing details), go back to Clarifier.
        if not result.is_valid():
            return AgentRoute.ClarifierAgent

        # If coming from Negotiator, loop back to Negotiator for re-evaluation.
        if state.get("backward") == AgentRoute.NegotiatorAgent:
            return AgentRoute.NegotiatorAgent

        # Default path forward after successful planning (from Clarifier, Risk, Validator)
        return AgentRoute.ScoperAgent
