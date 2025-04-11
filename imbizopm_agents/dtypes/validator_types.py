from typing import Dict, List, Literal

from pydantic import BaseModel, Field


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
