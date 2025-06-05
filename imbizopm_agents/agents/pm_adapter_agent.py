from typing import Any, Dict, Union  # Add Union

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..dtypes import ProjectSummary
from ..prompts.pm_adapter_prompts import (
    get_pm_adapter_output_format,
    get_pm_adapter_prompt,
)
from .base_agent import END, AgentState, BaseAgent
from .config import AgentDtypes, AgentRoute


class PMAdapterAgent(BaseAgent):
    """Agent that formats and exports the project plan for external tools."""

    def __init__(
        self,
        llm,
        use_structured_output: bool = False,
        use_two_step_generation: bool = True,
    ):
        model_cls = ProjectSummary if use_structured_output else None
        super().__init__(
            llm,
            name=AgentRoute.PMAdapterAgent,
            format_prompt=get_pm_adapter_output_format(),
            system_prompt=get_pm_adapter_prompt(),
            model_class=model_cls if not use_two_step_generation else ProjectSummary,
            prepare_input=self._prepare_input_logic,
            process_result=self._process_result_logic,
            next_step=self._next_step_logic,
            use_two_step_generation=use_two_step_generation,
        )

    def _prepare_input_logic(self, state: AgentState) -> str:
        """Prepares the input prompt by consolidating all previous agent outputs."""
        # Consolidate outputs from relevant agents into a comprehensive structure
        final_plan = {
            "project_definition": state.get(AgentRoute.ClarifierAgent, {}),
            "plan_components": getattr(
                state.get(AgentRoute.PlannerAgent), "components", {}
            ),  # Or Scoper
            "scope_mvp": state.get(
                AgentRoute.ScoperAgent, {}
            ),  # Include scope if available
            "tasks": getattr(state.get(AgentRoute.TaskifierAgent), "tasks", []),
            "timeline": state.get(AgentRoute.TimelineAgent, {}),
            "risk_assessment": state.get(AgentRoute.RiskAgent, {}),
            "validation": state.get(AgentRoute.ValidatorAgent, {}),
        }

        return f"""# Final Consolidated Project Plan Data:
{dumps_to_yaml(final_plan, indent=4)}

Format this consolidated project plan data into a final JSON output suitable for export or display. Ensure all key aspects (definition, plan, scope, tasks, timeline, risks, validation) are represented clearly. Strictly output only the JSON.
"""

    def _process_result_logic(
        self, state: AgentState, result: AgentDtypes.PMAdapterAgent
    ) -> AgentState:
        """Processes the result, setting the backward route."""
        state["backward"] = AgentRoute.PMAdapterAgent  # Store string
        # Potentially add the final formatted JSON to a specific key like 'final_output'
        state["final_output"] = result
        return state

    def _next_step_logic(
        self, state: AgentState, result: AgentDtypes.PMAdapterAgent
    ) -> str:  # Returns END string
        """Determines the next step, which is always END for this agent."""
        return END
