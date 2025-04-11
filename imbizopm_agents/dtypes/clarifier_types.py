from typing import List

from pydantic import BaseModel, Field


class ProjectPlan(BaseModel):
    refined_idea: str = Field(
        description="A clear, concise statement of what the project aims to accomplish"
    )
    goals: List[str] = Field(
        default_factory=list,
        description="A list of specific, measurable goals that address core needs with clear success criteria",
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="A list of specific limitations or boundaries that must be respected during the project",
    )
    
    @staticmethod
    def example() -> dict:
        """Return an example JSON representation of the ProjectPlan model."""
        return {
            "refined_idea": "Develop a mobile application that helps users track and reduce their carbon footprint through daily habit changes",
            "goals": [
                "Create a user-friendly interface that allows users to log daily activities",
                "Implement a carbon footprint calculator that provides real-time feedback",
                "Design a gamified reward system to incentivize sustainable behaviors",
                "Achieve 10,000 active users within 6 months of launch"
            ],
            "constraints": [
                "The application must be completed within a 4-month timeframe",
                "The development budget is limited to $50,000",
                "The app must comply with GDPR and other data privacy regulations",
                "Must be compatible with both iOS and Android platforms"
            ]
        }
