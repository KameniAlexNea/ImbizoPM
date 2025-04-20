from typing import List, Optional

from pydantic import BaseModel, Field


# New model to pair issues and solutions
class ResolutionIssue(BaseModel):
    issue: str = Field(
        default="", description="A specific issue or point of disagreement."
    )  # Added default
    proposed_solution: Optional[str] = Field(
        None,
        description="A suggested resolution or compromise for this specific issue.",
    )


# Modified NegotiationDetails model
class NegotiationDetails(BaseModel):
    items: List[ResolutionIssue] = Field(
        default_factory=list,  # Added default_factory
        description="A list of issues and their proposed solutions.",
    )
    priorities: List[str] = Field(
        default_factory=list,  # Added default_factory
        description="Key aspects that should be prioritized when resolving the conflict (e.g., timeline, value, feasibility)",
    )


# Modified ConflictResolution model
class ConflictResolution(BaseModel):
    conflict_area: str = Field(
        default="scope",  # Added default
        description='The area of conflict being addressed, either "scope" or "plan".',
    )
    negotiation: NegotiationDetails = Field(  # Renamed from negotiation_details
        default_factory=NegotiationDetails,  # Added default_factory
        description="Structured details of the conflict, including issues, proposed solutions, and priorities.",
    )

    def is_scope_conflict(self) -> bool:
        """Checks if the conflict is related to the project scope."""
        return self.conflict_area.lower() == "scope" or (
            "scope" in self.conflict_area.lower()
            and "plan" not in self.conflict_area.lower()
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
        """Return a simpler example JSON representation of the ConflictResolution model."""
        return {
            "conflict_area": "plan",
            "negotiation": {
                "items": [
                    {
                        "issue": "The proposed timeline for Phase 1 is too short.",
                        "proposed_solution": "Extend Phase 1 deadline by two weeks and reduce scope slightly.",
                    },
                    {
                        "issue": "Budget allocation for testing seems insufficient.",
                        "proposed_solution": "Reallocate $500 from the design budget to testing.",
                    },
                    {
                        "issue": "Resource availability conflict for the lead developer in week 3.",
                        "proposed_solution": None,  # No proposed solution yet
                    },
                ],
                "priorities": [
                    "Meeting the overall project deadline.",
                    "Ensuring product quality through adequate testing.",
                    "Keeping the project within the allocated budget.",
                ],
            },
        }
