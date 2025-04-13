from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Task(BaseModel):
    id: str = Field(description="Unique identifier for the task")
    name: str = Field(description="Brief, descriptive name of the task")
    description: str = Field(
        description="Detailed description of what needs to be done"
    )
    deliverable: str = Field(
        description="Specific deliverable this task contributes to"
    )
    owner_role: str = Field(description="Role responsible for completing this task")
    estimated_effort: Literal["Low", "Medium", "High"] = Field(
        description="Estimated effort required to complete this task"
    )
    epic: str = Field(description="Name of the epic this task belongs to")
    phase: str = Field(description="Phase in which this task is to be executed")
    dependencies: List[str] = Field(description="List of task IDs this task depends on")


class MissingInfoDetails(BaseModel):
    unclear_aspects: List[str] = Field(
        description="Key points that are unclear and block task definition"
    )
    questions: List[str] = Field(
        description="Questions that must be answered to clarify the scope"
    )
    suggestions: List[str] = Field(
        description="Concrete suggestions to resolve ambiguity or missing details"
    )


class TaskPlan(BaseModel):
    missing_info_details: Optional[MissingInfoDetails] = Field(
        description="Details about what information is missing and how to address it"
    )
    missing_info: bool = Field(
        description="Flag indicating that important task-related information is missing",
    )
    tasks: List[Task] = Field(
        description="List of defined tasks",
    )

    @staticmethod
    def example() -> dict:
        return {
            "complete_plan": {
                "tasks": [
                    {
                        "id": "TASK-001",
                        "name": "Create user authentication API",
                        "description": "Develop RESTful API endpoints for user registration, login, password reset, and account management",
                        "deliverable": "Authentication Microservice",
                        "owner_role": "Backend Developer",
                        "estimated_effort": "Medium",
                        "epic": "User Authentication System",
                        "phase": "Development",
                        "dependencies": [],
                    },
                    {
                        "id": "TASK-002",
                        "name": "Design user authentication flows",
                        "description": "Create wireframes and visual designs for login, registration, and account recovery screens",
                        "deliverable": "UI Design Package",
                        "owner_role": "UX Designer",
                        "estimated_effort": "Low",
                        "epic": "User Authentication System",
                        "phase": "Design",
                        "dependencies": [],
                    },
                    {
                        "id": "TASK-003",
                        "name": "Implement frontend authentication components",
                        "description": "Develop React components for all authentication screens and integrate with authentication API",
                        "deliverable": "Frontend Authentication Module",
                        "owner_role": "Frontend Developer",
                        "estimated_effort": "Medium",
                        "epic": "User Authentication System",
                        "phase": "Development",
                        "dependencies": ["TASK-001", "TASK-002"],
                    },
                    {
                        "id": "TASK-004",
                        "name": "Implement user permission system",
                        "description": "Design and implement role-based access control system with configurable permissions",
                        "deliverable": "Authorization Microservice",
                        "owner_role": "Backend Developer",
                        "estimated_effort": "High",
                        "epic": "User Authentication System",
                        "phase": "Development",
                        "dependencies": ["TASK-001"],
                    },
                    {
                        "id": "TASK-005",
                        "name": "Create automated test suite for authentication",
                        "description": "Develop comprehensive unit and integration tests for all authentication functionality",
                        "deliverable": "Authentication Test Suite",
                        "owner_role": "QA Engineer",
                        "estimated_effort": "Medium",
                        "epic": "User Authentication System",
                        "phase": "Testing",
                        "dependencies": ["TASK-001", "TASK-003", "TASK-004"],
                    },
                ],
                "missing_info": False,
                "missing_info_details": {
                    "unclear_aspects": [],
                    "questions": [],
                    "suggestions": [],
                },
            },
            "missing_plan": {
                "missing_info": True,
                "missing_info_details": {
                    "unclear_aspects": [
                        "The project scope does not specify which user roles need to be supported",
                        "Integration requirements with existing systems are not defined",
                        "Performance requirements and expected user load are not specified",
                        "Security requirements and compliance standards are not detailed",
                    ],
                    "questions": [
                        "What user roles need to be supported in the authentication system?",
                        "Which existing systems need to integrate with the new authentication service?",
                        "What is the expected peak user load for authentication services?",
                        "Are there specific security certifications or compliance standards that must be met?",
                        "Is single sign-on (SSO) functionality required? If so, which providers?",
                    ],
                    "suggestions": [
                        "Conduct a stakeholder workshop to define user roles and permissions",
                        "Request documentation for existing systems that require integration",
                        "Perform load testing on current systems to establish performance baselines",
                        "Consult with the security team to identify compliance requirements",
                        "Create a technical specification document before proceeding with task definition",
                    ],
                },
                "tasks": [],
            },
        }
