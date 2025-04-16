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
        """Return an example JSON representation of the ProjectPlan model."""
        return {
            "refined_idea": "Develop a mobile application that helps users track and reduce their carbon footprint through daily habit changes",
            "constraints": [
                "The application must be completed within a 4-month timeframe",
                "The development budget is limited to $50,000",
                "The app must comply with GDPR and other data privacy regulations",
                "Must be compatible with both iOS and Android platforms",
            ],
            "objectives": [
                {
                    "goal": "Create a user-friendly interface that allows users to log daily activities",
                    "success_metrics": [
                        "User Satisfaction Rate: Target 95%, Measured via post-launch surveys",
                        "Task Completion Time: Average time to log an activity < 30 seconds, Measured via usability testing",
                    ],
                    "deliverables": [
                        "UI/UX Design Mockups: High-fidelity mockups for all user interface screens.",
                        "Frontend Application Code: Implemented frontend code for the user interface.",
                    ],
                },
                {
                    "goal": "Implement a carbon footprint calculator that provides real-time feedback",
                    "success_metrics": [
                        "Calculator Accuracy: Within 5% of established benchmarks, Measured via validation tests",
                        "Feedback Latency: Real-time feedback displayed < 1 second after input, Measured via performance testing",
                    ],
                    "deliverables": [
                        "Carbon Footprint Calculation Engine: Backend service that calculates carbon footprint based on user inputs.",
                        "API for Calculator: API endpoint for the frontend to interact with the calculation engine.",
                    ],
                },
                {
                    "goal": "Design a gamified reward system to incentivize sustainable behaviors",
                    "success_metrics": [
                        "User Engagement Increase: Target 20% increase in daily active users within 3 months, Measured via analytics platform",
                        "Reward Redemption Rate: Target 15% of eligible users redeem rewards monthly, Measured via system logs",
                    ],
                    "deliverables": [
                        "Gamification Logic Design: Document outlining points, badges, leaderboards, and reward structure.",
                        "Reward System Implementation: Backend and frontend code for the gamified reward system.",
                    ],
                },
                {
                    "goal": "Achieve 10,000 active users within 6 months of launch",
                    "success_metrics": [
                        "Active User Count: Reach 10,000 monthly active users, Measured via analytics platform",
                        "User Acquisition Cost: Maintain average CAC below $2, Measured via marketing campaign data",
                    ],
                    "deliverables": [
                        "Marketing and Launch Plan: Strategy document for user acquisition and app launch.",
                        "Deployed Application (iOS & Android): The final application available on app stores.",
                    ],
                },
            ],
        }
