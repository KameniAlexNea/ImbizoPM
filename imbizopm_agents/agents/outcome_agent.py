from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..dtypes.outcome_types import ProjectSuccessCriteria
from ..prompts.outcome_prompts import (
    get_outcome_output_format,
    get_outcome_prompt,
)
from .agent_routes import AgentRoute
from .utils import format_list

OUTCOME_OUTPUT = get_outcome_output_format()

OUTCOME_PROMPT = get_outcome_prompt()


class OutcomeAgent(BaseAgent):
    """Agent that defines success metrics and deliverables."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.OutcomeAgent,
            OUTCOME_PROMPT,
            OUTCOME_OUTPUT,
            ProjectSuccessCriteria if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""Refined idea:
{state['idea'].get('refined', '')}
Goals:
{format_list(state.get('goals', []))}
Constraints:
{format_list(state.get('constraints', []))}

Define success metrics and deliverables."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        # Extract data with more robust error handling
        success_metrics = result.get("success_metrics", [])
        deliverables = result.get("deliverables", [])

        # Add the data to state
        state["outcomes"] = success_metrics
        state["deliverables"] = deliverables

        # Determine next step based on presence of outcomes
        state["next"] = (
            AgentRoute.PlannerAgent if success_metrics else AgentRoute.ClarifierAgent
        )
        state["current"] = AgentRoute.OutcomeAgent

        return state
