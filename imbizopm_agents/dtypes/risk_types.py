from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

Literal[
        "Technical", "Resource", "Timeline", "External", "Stakeholder"
    ]
class Risk(BaseModel):
    description: str = Field(description="Detailed description of the risk")
    category: str = Field(description="Category of the risk. E.g., Technical, Resource, Timeline, External, Stakeholder, etc.")
    impact: Literal["High", "Medium", "Low"] = Field(
        description="Impact level if the risk materializes"
    )
    probability: Literal["High", "Medium", "Low"] = Field(
        description="Assessed likelihood of the risk occurring (High, Medium, or Low)"
    )
    priority: Literal["High", "Medium", "Low"] = Field(
        description="Risk priority based on impact and probability"
    )
    mitigation_strategy: str = Field(
        description="Specific actions to reduce or prevent the risk"
    )
    contingency_plan: str = Field(description="Backup plan if the risk actually occurs")


class FeasibilityAssessment(BaseModel):
    risks: List[Risk] = Field(
        description="List of identified risks with mitigation and contingency strategies"
    )
    assumptions: List[str] = Field(
        description="List of critical assumptions underlying the feasibility analysis"
    )
    feasibility_concerns: List[str] = Field(
        description="Areas that may threaten feasibility along with recommendations"
    )
    dealbreakers: List[str] = Field(
        description="List of critical, blocking issues with possible solutions"
    )
    feasible: bool = Field(description="Overall feasibility status")

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
        """Return examples of both feasible and not feasible assessments."""
        return {
            "feasible_assessment_example": {
                "feasible": True,
                "risks": [
                    {
                        "description": "Vendor may not deliver critical components on time",
                        "category": "External",
                        "impact": "High",
                        "probability": "Medium",
                        "priority": "High",
                        "mitigation_strategy": "Identify backup vendors and establish clear delivery timelines with penalties for delays",
                        "contingency_plan": "Maintain buffer inventory and prepare alternative sourcing routes",
                    },
                    {
                        "description": "Key technical expertise may be unavailable during implementation",
                        "category": "Resource",
                        "impact": "High",
                        "probability": "Low",
                        "priority": "Medium",
                        "mitigation_strategy": "Cross-train team members and document knowledge sharing sessions",
                        "contingency_plan": "Establish contracts with external consultants who can be engaged on short notice",
                    },
                ],
                "assumptions": [
                    "Current infrastructure can support the increased load",
                    "Regulatory approval will be granted within 30 days of submission",
                    "The target user base has sufficient technical proficiency",
                ],
                "feasibility_concerns": [
                    "Technology Integration: The new system requires integration with legacy systems that have limited documentation. Recommendation: Conduct a technical spike.",
                    "Market Timing: Competitor products may launch before our release date. Recommendation: Prioritize differentiating features.",
                ],
                "dealbreakers": [],
            },
            "not_feasible_assessment_example": {
                "feasible": False,
                "risks": [],
                "assumptions": [],
                "feasibility_concerns": [],
                "dealbreakers": [
                    "Critical dependency on third-party API that is being deprecated. Impact: Core functionality cannot be delivered. Solution: Rebuild in-house (adds 4-6 months).",
                    "Compliance requirements cannot be met with the current technical approach. Impact: Violates regulations. Solution: Redesign architecture.",
                ],
            },
        }
