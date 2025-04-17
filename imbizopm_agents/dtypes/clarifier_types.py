from typing import List

from pydantic import BaseModel, Field


class ProjectObjective(BaseModel):
    goal: str = Field(
        description="A specific, measurable goal that addresses core needs with clear success criteria."
    )
    success_metrics: List[str] = Field(
        default_factory=list,
        description="List of specific measurements indicating achievement for this goal (e.g., metric, target value, method).",
    )
    deliverables: List[str] = Field(
        default_factory=list,
        description="List of key deliverables (as strings) required to achieve this specific goal.",
    )


class ProjectPlan(BaseModel):
    refined_idea: str = Field(
        default="",
        description="A clear, concise statement of what the project aims to accomplish",
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="A list of specific limitations or boundaries that must be respected during the project",
    )
    objectives: List[ProjectObjective] = Field(
        default_factory=list,
        description="A list of project objectives, each containing a goal, success metrics, and deliverables.",
    )

    def to_structured_string(self) -> str:
        """Formats the project plan into a structured string for the next agent."""
        output = f"**Refined Project Idea:**\n{self.refined_idea}\n\n"

        if self.constraints:
            output += "**Constraints:**\n"
            for constraint in self.constraints:
                output += f"- {constraint}\n"
            output += "\n"

        if self.objectives:
            output += "**Project Objectives:**\n"
            for i, objective in enumerate(self.objectives, 1):
                output += f"\n**Objective {i}: {objective.goal}**\n"
                if objective.success_metrics:
                    output += "  *Success Metrics:*\n"
                    for metric in objective.success_metrics:
                        output += f"    - {metric}\n"
                if objective.deliverables:
                    output += "  *Key Deliverables:*\n"
                    for deliverable in objective.deliverables:
                        output += f"    - {deliverable}\n"
            output += "\n"

        return output.strip()

    @staticmethod
    def example() -> dict:
        """Return a simpler example JSON representation of the ProjectPlan model."""
        return {
            "refined_idea": "Develop a simple website for a local bakery.",
            "constraints": [
                "Budget: $1000",
                "Timeline: 4 weeks",
                "Must include an online menu page.",
            ],
            "objectives": [
                {
                    "goal": "Launch a basic informational website.",
                    "success_metrics": [
                        "Website is live and accessible by the deadline.",
                        "Menu page accurately reflects current offerings.",
                    ],
                    "deliverables": [
                        "Website design mock-up.",
                        "Deployed website.",
                        "Content for the menu page.",
                    ],
                },
                {
                    "goal": "Ensure the website is mobile-friendly.",
                    "success_metrics": [
                        "Website renders correctly on common mobile devices (iOS/Android).",
                    ],
                    "deliverables": ["Responsive website code."],
                },
            ],
        }
