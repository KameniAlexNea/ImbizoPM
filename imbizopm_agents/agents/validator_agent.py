import json
from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..dtypes.validator_types import PlanValidation
from ..prompts.validator_prompts import (
    get_validator_output_format,
    get_validator_prompt,
)
from .agent_routes import AgentRoute


class ValidatorAgent(BaseAgent):
    """Agent that verifies alignment between idea, plan, and goals."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            "Validator",
            get_validator_prompt(),
            get_validator_output_format(),
            PlanValidation if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""# Idea and Goals
Refined idea:\n {json.dumps(state['idea'].get('refined', ''), indent=2)}
Goals:\n {json.dumps(state['goals'], indent=2)}
Constraints:\n {json.dumps(state['constraints'], indent=2)}
Outcomes:\n {json.dumps(state['outcomes'], indent=2)}

# Plan and Task
Plan:\n {json.dumps(state['plan'], indent=2)}
Scope:\n {json.dumps(state['scope'], indent=2)}
Tasks:\n {json.dumps(state['tasks'], indent=2)}

Validate alignment between the idea, goals, and the resulting plan. Stricly output only the JSON, to the appropriate format."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["validation"] = {
            "goals_alignment": result.get("goals_alignment", {}),
            "constraints_respected": result.get("constraints_respected", {}),
            "outcomes_achievable": result.get("outcomes_achievable", {}),
            "completeness_assessment": result.get("completeness_assessment", {}),
            "overall": result.get("overall_validation", True),
        }

        # Check validation result
        state["next"] = (
            AgentRoute.PMAdapterAgent
            if state["validation"]["overall"]
            else AgentRoute.PlannerAgent
        )
        state["current"] = AgentRoute.ValidatorAgent
        return state
