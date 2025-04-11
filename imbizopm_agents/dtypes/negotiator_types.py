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

    @staticmethod
    def example() -> dict:
        """Return an example JSON representation of the ConflictResolution model."""
        return {
            "conflict_area": "scope",
            "negotiation_details": {
                "issues": [
                    "Feature X exceeds original project boundaries",
                    "Stakeholders disagree on the priority of mobile vs. desktop features",
                    "Technical limitations make certain requested features difficult to implement",
                ],
                "proposed_solutions": [
                    "Reduce scope of Feature X to core functionality only",
                    "Phase implementation with mobile features in first release",
                    "Use alternative technical approach that satisfies 80% of requirements",
                ],
                "priorities": [
                    "Maintaining original timeline",
                    "Ensuring core user needs are addressed",
                    "Balancing technical feasibility with stakeholder expectations",
                ],
            },
        }
