from typing import List

from pydantic import BaseModel, Field


class Deliverable(BaseModel):
    name: str = Field(description="Clear name of the deliverable")
    description: str = Field(
        description="Detailed description of what this deliverable includes"
    )


class ProjectSuccessCriteria(BaseModel):
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
        """Return an example JSON representation of the ProjectSuccessCriteria model."""
        return {
            "success_metrics": [
                "95% user satisfaction rate measured through post-launch surveys",
                "50% reduction in processing time compared to previous system",
                "20% increase in user engagement within first 3 months",
                "Zero critical security vulnerabilities in penetration testing"
            ],
            "deliverables": [
                {
                    "name": "User Authentication System",
                    "description": "A secure login system with multi-factor authentication capability and password recovery functionality"
                },
                {
                    "name": "Analytics Dashboard",
                    "description": "An interactive dashboard displaying key performance metrics with customizable views and export capabilities"
                },
                {
                    "name": "API Documentation",
                    "description": "Comprehensive documentation of all API endpoints including request/response formats, authentication requirements, and example code"
                },
                {
                    "name": "Deployment Guide",
                    "description": "Step-by-step instructions for system deployment in various environments with troubleshooting information"
                }
            ]
        }
