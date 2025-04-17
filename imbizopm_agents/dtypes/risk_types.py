from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Risk(BaseModel):
    description: str = Field(default="", description="Detailed description of the risk")
    category: str = Field(
        default="",
        description="Category of the risk. E.g., Technical, Resource, Timeline, External, Stakeholder, etc.",
    )
    impact: str = Field(
        default="Low",
        description="Impact level if the risk materializes. (High, Medium, Low)",
    )
    probability: str = Field(
        default="Low",
        description="Assessed likelihood of the risk occurring (High, Medium, or Low)",
    )
    priority: str = Field(
        default="Low", description="Risk priority based on impact and probability"
    )
    mitigation_strategy: str = Field(
        default="", description="Specific actions to reduce or prevent the risk"
    )
    contingency_plan: str = Field(
        default="", description="Backup plan if the risk actually occurs"
    )


class FeasibilityAssessment(BaseModel):
    risks: List[Risk] = Field(
        default_factory=list,
        description="List of identified risks with mitigation and contingency strategies",
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="List of critical assumptions underlying the feasibility analysis",
    )
    feasibility_concerns: List[str] = Field(
        default_factory=list,
        description="Areas that may threaten feasibility along with recommendations",
    )
    dealbreakers: List[str] = Field(
        default_factory=list,
        description="List of critical, blocking issues with possible solutions",
    )
    feasible: bool = Field(default=False, description="Overall feasibility status")

    def to_structured_string(self) -> str:
        """Formats the feasibility assessment into a structured string."""
        if self.feasible:
            output = "**Feasibility Assessment: Feasible**\n\n"

            if self.risks:
                output += "**Identified Risks:**\n"
                for risk in self.risks:
                    output += f"- **Description:** {risk.description}\n"
                    output += f"  - **Category:** {risk.category}\n"
                    output += f"  - **Impact:** {risk.impact}, **Probability:** {risk.probability}, **Priority:** {risk.priority}\n"
                    output += f"  - **Mitigation:** {risk.mitigation_strategy}\n"
                    output += f"  - **Contingency:** {risk.contingency_plan}\n"
                output += "\n"

            if self.assumptions:
                output += "**Critical Assumptions:**\n"
                for assumption in self.assumptions:
                    output += f"- {assumption}\n"
                output += "\n"

            if self.feasibility_concerns:
                output += "**Feasibility Concerns & Recommendations:**\n"
                for concern in self.feasibility_concerns:
                    output += f"- {concern}\n"
                output += "\n"

        else:
            output = "**Feasibility Assessment: Not Feasible**\n\n"
            if self.dealbreakers:
                output += "**Dealbreakers (Blocking Issues):**\n"
                for dealbreaker in self.dealbreakers:
                    output += f"- {dealbreaker}\n"
                output += "\n"
            else:
                output += "No specific dealbreakers listed, but the project is deemed not feasible based on overall assessment.\n"

        return output.strip()

    @staticmethod
    def example() -> Dict[str, Any]:
        """Return simpler examples of both feasible and not feasible assessments."""
        return {
            "feasible_assessment_example": {
                "feasible": True,
                "risks": [
                    {
                        "description": "Delay in getting design approvals.",
                        "category": "Timeline",
                        "impact": "Medium",
                        "probability": "Medium",
                        "priority": "Medium",
                        "mitigation_strategy": "Schedule regular design review meetings.",
                        "contingency_plan": "Allocate buffer time in the schedule.",
                    },
                    {
                        "description": "Developer availability might be limited.",
                        "category": "Resource",
                        "impact": "High",
                        "probability": "Low",
                        "priority": "Medium",
                        "mitigation_strategy": "Confirm developer schedule in advance.",
                        "contingency_plan": "Identify backup developer.",
                    },
                ],
                "assumptions": [
                    "Budget of $1000 is approved.",
                    "Bakery owner can provide content promptly.",
                ],
                "feasibility_concerns": [
                    "Timeline is tight (4 weeks). Recommendation: Prioritize essential features only.",
                ],
                "dealbreakers": [],
            },
            "not_feasible_assessment_example": {
                "feasible": False,
                "risks": [],
                "assumptions": [],
                "feasibility_concerns": [],
                "dealbreakers": [
                    "Required budget ($5000) significantly exceeds allocated budget ($1000). Solution: Seek additional funding or drastically reduce scope.",
                    "Core feature requires technology incompatible with current hosting. Solution: Find new hosting provider or change feature.",
                ],
            },
        }
