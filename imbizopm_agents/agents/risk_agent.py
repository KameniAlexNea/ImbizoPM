import json
from typing import Any, Dict, List, Literal, Union

from pydantic import BaseModel, Field

from ..prompts.risk_prompts import get_risk_prompt, get_risk_output_format

from ..base_agent import AgentState, BaseAgent
from ..dtypes.common import Risk
from ..dtypes.risk_types import (
    Dealbreaker,
    FeasibilityAssessment,
    FeasibilityAssessmentBase,
    FeasibilityConcern,
    FeasibleAssessment,
    NotFeasibleAssessment,
)
from .agent_routes import AgentRoute


RISK_OUTPUT = get_risk_output_format()

RISK_PROMPT = get_risk_prompt()


class RiskAgent(BaseAgent):
    """Agent that reviews feasibility and spots contradictions."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            "Risk",
            RISK_PROMPT,
            RISK_OUTPUT,
            FeasibilityAssessment if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""
Refined idea: {state.get('idea', {}).get('refined', '')}
Goals: {json.dumps(state.get('goals', []), indent=2)}
Constraints: {json.dumps(state.get('constraints', []), indent=2)}

Plan: {json.dumps(state.get("plan", {}), indent=2)}
Scope: {json.dumps(state.get("scope", {}), indent=2)}
Tasks: {json.dumps(state.get("tasks", []), indent=2)}
Timeline: {json.dumps(state.get("timeline", {}), indent=2)}

Assess risks and overall feasibility. You should output a JSON format"""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["risks"] = result.get("risks", [])
        state["assumptions"] = result.get("assumptions", [])
        state["feasibility_concerns"] = result.get("feasibility_concerns", [])
        if "warn_errors" not in state:
            state["warn_errors"] = {}
        state["warn_errors"]["dealbreakers"] = result.get("dealbreakers", [])
        state["next"] = (
            AgentRoute.ValidatorAgent
            if result.get("feasible", True) or not state["dealbreakers"]
            else AgentRoute.PlannerAgent
        )
        state["current"] = AgentRoute.RiskAgent
        return state
