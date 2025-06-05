from collections import defaultdict
from typing import Dict, List

from pydantic import BaseModel, Field


class NamedItem(BaseModel):
    name: str = Field(
        default="",  # Added default
        description="Name of the item, such as a project phase, epic, or strategy",
    )
    description: str = Field(
        default="",  # Added default
        description="Detailed explanation providing context, objectives, or value of the named item",
    )
    kind: str = Field(
        default="phase",  # Added default
        description="Type of item, indicating whether it is a phase, epic, or strategy. (phase, epic, strategy)",
    )


class VagueDetails(BaseModel):
    unclear_aspects: List[str] = Field(
        default_factory=list,
        description="List of specific aspects of the project that lack sufficient clarity",
    )
    questions: List[str] = Field(
        default_factory=list,
        description="Clarifying questions that need to be answered before planning can proceed",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Concrete suggestions to resolve ambiguity and improve clarity",
    )


class ProjectPlanOutput(BaseModel):
    too_vague: bool = Field(
        default=False,  # Added default
        description="Indicates whether the project is too vague to generate a meaningful plan",
    )
    vague_details: VagueDetails = Field(
        default_factory=VagueDetails,
        description="Details of the vagueness including unclear aspects, questions, and suggestions for clarification",
    )
    components: List[NamedItem] = Field(
        default_factory=list,
        description="Collection of items which can be phases, epics, or strategies, providing an integrated view of all planning elements",
    )

    def is_valid(self) -> bool:
        """Check if the project plan is valid."""
        return (
            not self.too_vague
            or self.components is None
            and not self.vague_details.unclear_aspects
        )

    def to_structured_string(self) -> str:
        """Formats the project plan output into a structured string."""
        if self.too_vague:
            output = "**Project Plan Status: Too Vague**\n\n"
            output += "The project description lacks sufficient detail for planning. Please address the following:\n\n"

            if self.vague_details.unclear_aspects:
                output += "**Unclear Aspects:**\n"
                for aspect in self.vague_details.unclear_aspects:
                    output += f"- {aspect}\n"
                output += "\n"

            if self.vague_details.questions:
                output += "**Questions to Address:**\n"
                for question in self.vague_details.questions:
                    output += f"- {question}\n"
                output += "\n"

            if self.vague_details.suggestions:
                output += "**Suggestions for Clarification:**\n"
                for suggestion in self.vague_details.suggestions:
                    output += f"- {suggestion}\n"
                output += "\n"
        else:
            output = "**Project Plan Components:**\n\n"
            if not self.components:
                output += "No specific components were generated.\n"
            else:
                # Group components by kind
                grouped_components: Dict[str, List[NamedItem]] = defaultdict(list)
                for component in self.components:
                    grouped_components[component.kind].append(component)

                # Define the order for display
                kind_order = ["phase", "epic", "strategy"]

                for kind in kind_order:
                    if kind in grouped_components:
                        output += f"**{kind.capitalize()}s:**\n"
                        for item in grouped_components[kind]:
                            output += f"- **{item.name}:** {item.description}\n"
                        output += "\n"

        return output.strip()

    @staticmethod
    def example() -> dict:
        """Return a simpler example JSON representation of the ProjectPlanOutput model."""
        return {
            "not_too_vague_project": {
                "too_vague": False,
                "vague_details": {
                    "unclear_aspects": [],
                    "questions": [],
                    "suggestions": [],
                },
                "components": [
                    {
                        "name": "Phase 1: Setup",
                        "description": "Initial project setup",
                        "kind": "phase",
                    },
                    {
                        "name": "User Login",
                        "description": "Allow users to sign in",
                        "kind": "epic",
                    },
                    {
                        "name": "Iterative Development",
                        "description": "Use sprints",
                        "kind": "strategy",
                    },
                ],
            },
            "too_vague_project": {
                "too_vague": True,
                "vague_details": {
                    "unclear_aspects": ["Features not defined"],
                    "questions": ["What features are required?"],
                    "suggestions": ["Define feature list"],
                },
                "components": [],
            },
        }
