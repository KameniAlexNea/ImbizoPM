from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# New model to pair issues and solutions
class ResolutionIssue(BaseModel):
    issue: str = Field(description="A specific issue or point of disagreement.")
    proposed_solution: Optional[str] = Field(
        None,
        description="A suggested resolution or compromise for this specific issue.",
    )


# Modified NegotiationDetails model
class NegotiationDetails(BaseModel):
    items: List[ResolutionIssue] = Field(
        description="A list of issues and their proposed solutions."
    )
    priorities: List[str] = Field(
        description="Key aspects that should be prioritized when resolving the conflict (e.g., timeline, value, feasibility)"
    )


# Modified ConflictResolution model
class ConflictResolution(BaseModel):
    conflict_area: Literal["scope", "plan"] = Field(
        description='The area of conflict being addressed, either "scope" or "plan".'
    )
    negotiation: NegotiationDetails = Field(  # Renamed from negotiation_details
        description="Structured details of the conflict, including issues, proposed solutions, and priorities."
    )

    def to_structured_string(self) -> str:
        """Formats the conflict resolution details into a structured string."""
        output = f"**Conflict Area:** {self.conflict_area.capitalize()}\n\n"

        output += "**Negotiation Details:**\n"

        if self.negotiation.items:
            output += "*   **Issues & Proposed Solutions:**\n"
            for item in self.negotiation.items:
                solution_text = (
                    f" -> Proposed Solution: {item.proposed_solution}"
                    if item.proposed_solution
                    else " -> No solution proposed yet"
                )
                output += f"    - Issue: {item.issue}{solution_text}\n"
            output += "\n"

        if self.negotiation.priorities:
            output += "*   **Priorities:**\n"
            for priority in self.negotiation.priorities:
                output += f"    - {priority}\n"
            output += "\n"

        return output.strip()

    @staticmethod
    def example() -> dict:
        """Return an example JSON representation of the ConflictResolution model."""
        return {
            "conflict_area": "scope",
            "negotiation": {  # Updated field name
                "items": [  # Updated structure for issues/solutions
                    {
                        "issue": "Feature X exceeds original project boundaries",
                        "proposed_solution": "Reduce scope of Feature X to core functionality only",
                    },
                    {
                        "issue": "Stakeholders disagree on the priority of mobile vs. desktop features",
                        "proposed_solution": "Phase implementation with mobile features in first release",
                    },
                    {
                        "issue": "Technical limitations make certain requested features difficult to implement",
                        "proposed_solution": "Use alternative technical approach that satisfies 80% of requirements",
                    },
                    {
                        "issue": "Unclear requirements for reporting module"
                    },  # Example issue without a proposed solution yet
                ],
                "priorities": [
                    "Maintaining original timeline",
                    "Ensuring core user needs are addressed",
                    "Balancing technical feasibility with stakeholder expectations",
                ],
            },
        }
