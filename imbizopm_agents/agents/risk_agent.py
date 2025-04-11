import json
from typing import Any, Dict, List, Literal, Union

from pydantic import BaseModel, Field

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute

# Risk and feasibility-related dataclasses


class Risk(BaseModel):
    description: str
    category: Literal["Technical", "Resource", "Timeline", "External", "Stakeholder"]
    impact: Literal["High", "Medium", "Low"]
    probability: Literal["High", "Medium", "Low"]
    priority: Literal["High", "Medium", "Low"]
    mitigation_strategy: str
    contingency_plan: str


class FeasibilityConcern(BaseModel):
    area: str
    description: str
    recommendation: str


class Dealbreaker(BaseModel):
    description: str
    impact: str
    potential_solution: str


# Base class (used for typing clarity, not strictly necessary)


class FeasibilityAssessmentBase(BaseModel):
    risks: List[Risk] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    feasibility_concerns: List[FeasibilityConcern] = Field(default_factory=list)


# Feasible case


class FeasibleAssessment(FeasibilityAssessmentBase):
    feasible: Literal[True] = True


# Not feasible case


class NotFeasibleAssessment(FeasibilityAssessmentBase):
    feasible: Literal[False] = False
    dealbreakers: List[Dealbreaker] = Field(default_factory=list)


# Union type if you'd like to work with either
FeasibilityAssessment = Union[FeasibleAssessment, NotFeasibleAssessment]


RISK_OUTPUT = """OUTPUT FORMAT:
{{
    "feasible": true,
    "risks": [
        {{
            "description": "Detailed description of the risk",
            "category": "Technical/Resource/Timeline/External/Stakeholder",
            "impact": "High/Medium/Low",
            "probability": "High/Medium/Low",
            "priority": "High/Medium/Low",
            "mitigation_strategy": "Specific actions to reduce risk",
            "contingency_plan": "What to do if the risk materializes"
        }},
        "..."
    ],
    "assumptions": [
        "Critical assumption that impacts project success",
        "..."
    ],
    "feasibility_concerns": [
        {{
            "area": "Specific area of concern",
            "description": "Detailed description of why this is a concern",
            "recommendation": "How to address this concern"
        }},
        "..."
    ]
}}

// Alternative output if project is not feasible:
{{
    "feasible": false,
    "dealbreakers": [
        {{
            "description": "Critical issue that makes the project unfeasible",
            "impact": "Why this is a dealbreaker",
            "potential_solution": "Possible way to address this issue"
        }},
        "..."
    ],
    "risks": [...],
    "assumptions": [...],
    "feasibility_concerns": [...]
}}"""

RISK_PROMPT = f"""You are the Risk Agent. Your job is to identify potential risks, assess the project's feasibility, and develop mitigation strategies.

PROCESS:
1. Review the entire project plan, timeline, and tasks
2. Identify potential risks that could impact success
3. Assess the impact and probability of each risk
4. Develop specific mitigation strategies for high-priority risks
5. Evaluate the overall feasibility of the project plan
6. Look for contradictions or unrealistic aspects in the plan

GUIDELINES:
- Consider technical, resource, timeline, external dependency, and stakeholder risks
- Assess impact based on effect on goals, timeline, budget, and quality
- Probability should reflect realistic likelihood based on project context
- Mitigation strategies should be specific and actionable
- Feasibility assessment should consider team capabilities, resources, and constraints
- Identify any assumptions that may impact feasibility

{RISK_OUTPUT}"""


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
