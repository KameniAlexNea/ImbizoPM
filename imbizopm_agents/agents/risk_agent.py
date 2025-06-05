from typing import Union  # Add Union

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import FeasibilityAssessment
from ..prompts.risk_prompts import get_risk_output_format, get_risk_prompt
from .base_agent import AgentState, BaseAgent
from .config import AgentDtypes, AgentRoute


class RiskAgent(BaseAgent):
    """Agent that reviews feasibility and spots contradictions."""

    def __init__(
        self,
        llm,
        use_structured_output: bool = False,
        use_two_step_generation: bool = True,
    ):
        model_cls = FeasibilityAssessment if use_structured_output else None
        super().__init__(
            llm,
            name=AgentRoute.RiskAgent,
            format_prompt=get_risk_output_format(),
            system_prompt=get_risk_prompt(),
            model_class=(
                model_cls if not use_two_step_generation else FeasibilityAssessment
            ),
            prepare_input=self._prepare_input_logic,
            process_result=self._process_result_logic,
            next_step=self._next_step_logic,
            use_two_step_generation=use_two_step_generation,
        )

    def _prepare_input_logic(self, state: AgentState) -> str:
        """Prepares the input prompt using the plan, tasks, and timeline."""
        clarifier_output = state.get(AgentRoute.ClarifierAgent, {})
        planner_output = state.get(AgentRoute.PlannerAgent)  # Or Scoper if used
        taskifier_output = state.get(AgentRoute.TaskifierAgent)
        timeline_output = state.get(AgentRoute.TimelineAgent)

        plan_components = getattr(planner_output, "components", {})
        tasks = getattr(taskifier_output, "tasks", [])
        # Extract relevant timeline info (e.g., total duration, milestones)
        timeline_summary = {
            "estimated_duration": getattr(timeline_output, "estimated_duration", "N/A"),
            "milestones": getattr(timeline_output, "milestones", []),
        }

        return f"""# Clarified Project Details:
{dumps_to_yaml(clarifier_output, indent=4)}

# Plan Components:
{dumps_to_yaml(plan_components, indent=4)}

# Detailed Tasks:
{dumps_to_yaml(tasks, indent=4)}

# Estimated Timeline Summary:
{dumps_to_yaml(timeline_summary, indent=4)}

Assess the overall feasibility of the project based on the clarified goals, constraints, plan, tasks, and timeline. Identify potential risks, contradictions, or inconsistencies. Specifically highlight any "dealbreaker" risks that fundamentally challenge the project's viability. Output should be in JSON format.
"""

    def _process_result_logic(
        self, state: AgentState, result: AgentDtypes.RiskAgent
    ) -> AgentState:
        """Processes the result, setting the backward route."""
        state["backward"] = AgentRoute.RiskAgent  # Store string
        return state

    def _next_step_logic(
        self, state: AgentState, result: AgentDtypes.RiskAgent
    ) -> AgentRoute:
        """Determines the next agent based on feasibility and dealbreakers."""
        # If feasible or no dealbreakers, proceed to Validator
        if result.feasible or not result.dealbreakers:
            return AgentRoute.ValidatorAgent
        # Otherwise (not feasible due to dealbreakers), go back to Planner
        else:
            return AgentRoute.PlannerAgent
