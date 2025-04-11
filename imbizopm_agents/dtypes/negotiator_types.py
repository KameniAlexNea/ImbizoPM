from typing import List, Literal

from pydantic import BaseModel, Field


class NegotiationDetails(BaseModel):
    issues: List[str] = Field(
        default_factory=list,
        description="A list of specific issues or points of disagreement identified in the project plan",
    )
    proposed_solutions: List[str] = Field(
        default_factory=list,
        description="Suggested resolutions or compromises to address the identified issues",
    )
    priorities: List[str] = Field(
        default_factory=list,
        description="Key aspects that should be prioritized when resolving the conflict (e.g., timeline, value, feasibility)",
    )


class ConflictResolution(BaseModel):
    conflict_area: Literal["scope", "plan"] = Field(
        description='The area of conflict being addressed, either "scope" (project boundaries or features) or "plan" (timeline, resources, execution)'
    )
    negotiation_details: NegotiationDetails = Field(
        description="Structured details of the conflict, including issues, proposed solutions, and priorities for resolution"
    )
