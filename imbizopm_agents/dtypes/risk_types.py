from typing import Any, Dict, List, Literal, Union

from pydantic import BaseModel, Field


class Risk(BaseModel):
    description: str = Field(description="Detailed description of the risk")
    category: Literal[
        "Technical", "Resource", "Timeline", "External", "Stakeholder"
    ] = Field(description="Category of the risk")
    impact: Literal["High", "Medium", "Low"] = Field(
        description="Impact level if the risk materializes"
    )
    probability: Literal["High", "Medium", "Low"] = Field(
        description="Likelihood of the risk occurring"
    )
    priority: Literal["High", "Medium", "Low"] = Field(
        description="Risk priority based on impact and probability"
    )
    mitigation_strategy: str = Field(
        description="Specific actions to reduce or prevent the risk"
    )
    contingency_plan: str = Field(description="Backup plan if the risk actually occurs")


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
    dealbreakers: List[Dealbreaker] = Field(
        default_factory=list,
        description="List of critical, blocking issues with possible solutions",
    )
    feasible: Literal[True] = Field(
        default=True, description="Set to True when the project is considered feasible"
    )


class FeasibilityAssessment(FeasibilityAssessmentBase):
    @staticmethod
    def example() -> Dict[str, Any]:
        """Return examples of both feasible and not feasible assessments."""
        return {
            "feasible_example": {
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
                    {
                        "area": "Technology Integration",
                        "description": "The new system requires integration with legacy systems that have limited documentation",
                        "recommendation": "Conduct a technical spike to assess integration complexity and allocate additional time for unexpected issues",
                    },
                    {
                        "area": "Market Timing",
                        "description": "Competitor products may launch before our release date",
                        "recommendation": "Prioritize differentiating features for initial release and accelerate go-to-market strategy",
                    },
                ],
                "dealbreakers": []
            },
            "not_feasible_example": {
                "feasible": False,
                "risks": [],
                "assumptions": [],
                "feasibility_concerns": [],
                "dealbreakers": [
                    {
                        "description": "Critical dependency on third-party API that is being deprecated",
                        "impact": "Without this API, core functionality cannot be delivered as specified",
                        "potential_solution": "Rebuild the required functionality in-house, adding 4-6 months to the timeline",
                    },
                    {
                        "description": "Compliance requirements cannot be met with the current technical approach",
                        "impact": "Project would violate regulatory requirements in key markets",
                        "potential_solution": "Redesign architecture to incorporate required security and privacy controls",
                    },
                ],
            },
        }
