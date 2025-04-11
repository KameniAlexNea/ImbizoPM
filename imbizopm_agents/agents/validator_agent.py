import json  # Add import for json module
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute


class GoalAlignment(BaseModel):
    aligned: Literal["Yes", "Partial", "No"] = Field(
        description="Whether the goal is fully, partially, or not aligned at all"
    )
    evidence: str = Field(
        description="Concrete elements of the plan showing alignment with the goal"
    )
    gaps: str = Field(
        description="Aspects of the goal not addressed in the current plan"
    )


class ConstraintRespect(BaseModel):
    respected: Literal["Yes", "Partial", "No"] = Field(
        description="Level to which the constraint is respected"
    )
    evidence: str = Field(
        description="Proof or reasoning showing respect for the constraint"
    )
    concerns: str = Field(
        description="Concerns or potential issues in respecting this constraint"
    )


class OutcomeAchievability(BaseModel):
    achievable: Literal["Yes", "Partial", "No"] = Field(
        description="Whether the outcome can reasonably be achieved"
    )
    evidence: str = Field(
        description="Justification for achievability based on the plan"
    )
    risks: str = Field(
        description="Risks or blockers that could hinder achieving the outcome"
    )


class CompletenessAssessment(BaseModel):
    missing_elements: List[str] = Field(
        default_factory=list,
        description="List of important elements missing from the plan",
    )
    improvement_suggestions: List[str] = Field(
        default_factory=list,
        description="Ideas or tips to improve the plan's completeness",
    )


class PlanValidation(BaseModel):
    overall_validation: bool = Field(
        description="True if the plan is validated overall, else False"
    )
    alignment_score: str = Field(
        description='Score between "0%" and "100%" indicating alignment strength'
    )
    goals_alignment: Dict[str, GoalAlignment] = Field(
        default_factory=dict,
        description="Mapping from goal names to their alignment evaluation",
    )
    constraints_respected: Dict[str, ConstraintRespect] = Field(
        default_factory=dict,
        description="Mapping from constraint names to their respect status",
    )
    outcomes_achievable: Dict[str, OutcomeAchievability] = Field(
        default_factory=dict,
        description="Mapping from outcome names to achievability assessment",
    )
    completeness_assessment: CompletenessAssessment = Field(
        default_factory=CompletenessAssessment,
        description="Summary of what's missing and how the plan could be improved",
    )


VALIDATOR_OUTPUT = """OUTPUT FORMAT:
{{
    "overall_validation": true, # or false
    "alignment_score": "0-100%",
    "goals_alignment": {{
        "Goal 1": {{
            "aligned": "Yes/Partial/No",
            "evidence": "Specific elements in the plan that address this goal",
            "gaps": "Any aspects of the goal not adequately addressed"
        }},
        "..."
    }},
    "constraints_respected": {{
        "Constraint 1": {{
            "respected": "Yes/Partial/No",
            "evidence": "How the plan respects this constraint",
            "concerns": "Any potential violations or risks"
        }},
        "..."
    }},
    "outcomes_achievable": {{
        "Outcome 1": {{
            "achievable": "Yes/Partial/No",
            "evidence": "Elements in the plan that will deliver this outcome",
            "risks": "Factors that might prevent achievement"
        }},
        "..."
    }},
    "completeness_assessment": {{
        "missing_elements": [
            "Specific element missing from the plan",
            "..."
        ],
        "improvement_suggestions": [
            "Specific suggestion to improve plan completeness",
            "..."
        ]
    }}
}}"""

VALIDATOR_PROMPT = f"""You are the Validator Agent. Your job is to verify that the final project plan aligns with the original goals, respects all constraints, and will deliver the expected outcomes.

PROCESS:
1. Compare the original idea and refined goals with the final plan
2. Check that all constraints are respected in the plan
3. Verify that the planned deliverables will achieve the desired outcomes
4. Assess the completeness and coherence of the overall plan
5. Identify any gaps or misalignments

GUIDELINES:
- Analyze each goal individually to verify the plan addresses it
- Check each constraint to ensure the plan respects its limitations
- Verify that success metrics are addressed by specific elements in the plan
- Look for logical inconsistencies or missing components
- Consider the project from stakeholder perspectives

{VALIDATOR_OUTPUT}"""


class ValidatorAgent(BaseAgent):
    """Agent that verifies alignment between idea, plan, and goals."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            "Validator",
            VALIDATOR_PROMPT,
            VALIDATOR_OUTPUT,
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
