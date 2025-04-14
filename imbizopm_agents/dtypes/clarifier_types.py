from typing import List

from pydantic import BaseModel, Field


class Deliverable(BaseModel):
    name: str = Field(description="Clear name of the deliverable")
    description: str = Field(
        description="Detailed description of what this deliverable includes"
    )


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
    success_metrics: List[str] = Field(
        default_factory=list,
        description="List of specific measurements that indicate goal achievement (e.g., target value, method of measurement)",
    )
    deliverables: List[Deliverable] = Field(
        default_factory=list,
        description="List of key deliverables, each defined by a name and detailed description",
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
                "Achieve 10,000 active users within 6 months of launch",
            ],
            "constraints": [
                "The application must be completed within a 4-month timeframe",
                "The development budget is limited to $50,000",
                "The app must comply with GDPR and other data privacy regulations",
                "Must be compatible with both iOS and Android platforms",
            ],
            "success_metrics": [
                "95% user satisfaction rate measured through post-launch surveys",
                "50% reduction in processing time compared to previous system",
                "20% increase in user engagement within first 3 months",
                "Zero critical security vulnerabilities in penetration testing",
            ],
            "deliverables": [
                {
                    "name": "User Authentication System",
                    "description": "A secure login system with multi-factor authentication capability and password recovery functionality",
                },
                {
                    "name": "Analytics Dashboard",
                    "description": "An interactive dashboard displaying key performance metrics with customizable views and export capabilities",
                },
                {
                    "name": "API Documentation",
                    "description": "Comprehensive documentation of all API endpoints including request/response formats, authentication requirements, and example code",
                },
                {
                    "name": "Deployment Guide",
                    "description": "Step-by-step instructions for system deployment in various environments with troubleshooting information",
                },
            ],
        }
