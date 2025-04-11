from typing import List, Literal, Union

from pydantic import BaseModel, Field

from .common import Risk


class FeasibilityConcern(BaseModel):
    area: str = Field(
        description="Specific area of concern (e.g., funding, technology, regulations)"
    )
    description: str = Field(
        description="Detailed explanation of why this area is a concern"
    )
    recommendation: str = Field(description="Suggested actions to address the concern")


class Dealbreaker(BaseModel):
    description: str = Field(description="Critical issue making the project unfeasible")
    impact: str = Field(
        description="Explanation of how this issue threatens feasibility"
    )
    potential_solution: str = Field(description="Proposed workaround or fix, if any")


class FeasibilityAssessmentBase(BaseModel):
    risks: List[Risk] = Field(
        default_factory=list,
        description="List of identified risks with mitigation and contingency strategies",
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="List of critical assumptions underlying the feasibility analysis",
    )
    feasibility_concerns: List[FeasibilityConcern] = Field(
        default_factory=list,
        description="Areas that may threaten feasibility along with recommendations",
    )


class FeasibleAssessment(FeasibilityAssessmentBase):
    feasible: Literal[True] = Field(
        default=True, description="Set to True when the project is considered feasible"
    )


class NotFeasibleAssessment(FeasibilityAssessmentBase):
    feasible: Literal[False] = Field(
        default=False,
        description="Set to False when the project is currently not feasible",
    )
    dealbreakers: List[Dealbreaker] = Field(
        default_factory=list,
        description="List of critical, blocking issues with possible solutions",
    )


FeasibilityAssessment = Union[FeasibleAssessment, NotFeasibleAssessment]
