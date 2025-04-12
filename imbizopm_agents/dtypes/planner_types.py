from typing import List

from pydantic import BaseModel, Field


class NamedDescription(BaseModel):
    name: str = Field(
        description="Name of the item, such as a project phase, epic, or strategy"
    )
    description: str = Field(
        description="Detailed explanation providing context, objectives, or value of the named item"
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
        description="Indicates whether the project is too vague to generate a meaningful plan"
    )
    vague_details: VagueDetails = Field(
        default_factory=VagueDetails,
        description="Details of the vagueness including unclear aspects, questions, and suggestions for clarification",
    )
    phases: List[NamedDescription] = Field(
        default_factory=list,
        description="List of key project phases with descriptive names and objectives",
    )
    epics: List[NamedDescription] = Field(
        default_factory=list,
        description="List of major epics describing significant chunks of functionality or value delivery",
    )
    strategies: List[NamedDescription] = Field(
        default_factory=list,
        description="List of strategic approaches or methodologies to be used in the project",
    )

    @staticmethod
    def example() -> dict:
        """Return an example JSON representation of the ProjectPlanOutput model."""
        return {
            "too_vague": False,
            "vague_details": {
                "unclear_aspects": [
                    "Target audience demographics need further specification",
                    "Integration requirements with existing systems",
                ],
                "questions": [
                    "What is the exact timeline for delivery of the first MVP?",
                    "Are there regulatory compliance requirements to consider?",
                ],
                "suggestions": [
                    "Conduct a stakeholder workshop to define target audience",
                    "Request documentation of current system APIs for integration planning",
                ],
            },
            "phases": [
                {
                    "name": "Discovery and Planning",
                    "description": "Research user needs, define requirements, and create detailed project roadmap",
                },
                {
                    "name": "Design and Architecture",
                    "description": "Create UX/UI designs and establish technical architecture for the solution",
                },
                {
                    "name": "Development",
                    "description": "Implement features according to specifications with regular quality checks",
                },
                {
                    "name": "Testing and Validation",
                    "description": "Perform comprehensive testing including unit, integration, and user acceptance testing",
                },
                {
                    "name": "Deployment and Launch",
                    "description": "Release the solution to production and support initial user adoption",
                },
            ],
            "epics": [
                {
                    "name": "User Authentication System",
                    "description": "Features related to user registration, login, profile management, and access control",
                },
                {
                    "name": "Data Management",
                    "description": "Core functionality for data input, storage, retrieval, and export capabilities",
                },
                {
                    "name": "Reporting Dashboard",
                    "description": "Interactive visualizations and analytics features to provide insights from user data",
                },
                {
                    "name": "Mobile Responsiveness",
                    "description": "Ensuring the application functions well on various mobile devices and screen sizes",
                },
            ],
            "strategies": [
                {
                    "name": "Agile Development",
                    "description": "Utilizing two-week sprints with daily standups to maintain velocity and address issues quickly",
                },
                {
                    "name": "Continuous Integration",
                    "description": "Implementing automated testing and deployment pipelines to ensure code quality",
                },
                {
                    "name": "User-Centered Design",
                    "description": "Involving target users throughout the design process with regular feedback sessions",
                },
                {
                    "name": "Phased Delivery",
                    "description": "Releasing core functionality first, followed by additional features in prioritized order",
                },
            ],
        }
