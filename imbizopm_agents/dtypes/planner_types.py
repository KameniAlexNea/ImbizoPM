from typing import List, Literal

from pydantic import BaseModel, Field


class NamedItem(BaseModel):
    name: str = Field(
        description="Name of the item, such as a project phase, epic, or strategy"
    )
    description: str = Field(
        description="Detailed explanation providing context, objectives, or value of the named item"
    )
    kind: Literal["phase", "epic", "strategy"] = Field(
        description="Type of item, indicating whether it is a phase, epic, or strategy"
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
    components: List[NamedItem] = Field(
        default_factory=list,
        description="Collection of items which can be phases, epics, or strategies, providing an integrated view of all planning elements",
    )

    @staticmethod
    def example() -> dict:
        """Return an example JSON representation of the ProjectPlanOutput model."""
        return {
            "not_too_vague_project": {
                "too_vague": False,
                "vague_details": {
                    "unclear_aspects": [],
                    "questions": [],
                    "suggestions": [],
                },
                "components": [
                    {
                        "name": "Discovery and Planning",
                        "description": "Research user needs, define requirements, and create detailed project roadmap",
                        "kind": "phase",
                    },
                    {
                        "name": "Design and Architecture",
                        "description": "Create UX/UI designs and establish technical architecture for the solution",
                        "kind": "phase",
                    },
                    {
                        "name": "Development",
                        "description": "Implement features according to specifications with regular quality checks",
                        "kind": "phase",
                    },
                    {
                        "name": "Testing and Validation",
                        "description": "Perform comprehensive testing including unit, integration, and user acceptance testing",
                        "kind": "phase",
                    },
                    {
                        "name": "Deployment and Launch",
                        "description": "Release the solution to production and support initial user adoption",
                        "kind": "phase",
                    },
                    {
                        "name": "User Authentication System",
                        "description": "Features related to user registration, login, profile management, and access control",
                        "kind": "epic",
                    },
                    {
                        "name": "Data Management",
                        "description": "Core functionality for data input, storage, retrieval, and export capabilities",
                        "kind": "epic",
                    },
                    {
                        "name": "Reporting Dashboard",
                        "description": "Interactive visualizations and analytics features to provide insights from user data",
                        "kind": "epic",
                    },
                    {
                        "name": "Mobile Responsiveness",
                        "description": "Ensuring the application functions well on various mobile devices and screen sizes",
                        "kind": "epic",
                    },
                    {
                        "name": "Agile Development",
                        "description": "Utilizing two-week sprints with daily standups to maintain velocity and address issues quickly",
                        "kind": "strategy",
                    },
                    {
                        "name": "Continuous Integration",
                        "description": "Implementing automated testing and deployment pipelines to ensure code quality",
                        "kind": "strategy",
                    },
                    {
                        "name": "User-Centered Design",
                        "description": "Involving target users throughout the design process with regular feedback sessions",
                        "kind": "strategy",
                    },
                    {
                        "name": "Phased Delivery",
                        "description": "Releasing core functionality first, followed by additional features in prioritized order",
                        "kind": "strategy",
                    },
                ],
            },
            "too_vague_project": {
                "too_vague": True,
                "vague_details": {
                    "unclear_aspects": [
                        "Target audience demographics need further specification",
                        "Integration requirements with existing systems",
                        "Scope of project is poorly defined",
                        "Budget constraints are not specified",
                    ],
                    "questions": [
                        "What is the exact timeline for delivery of the first MVP?",
                        "Are there regulatory compliance requirements to consider?",
                        "Who are the primary stakeholders for this project?",
                        "What are the primary success metrics for this initiative?",
                    ],
                    "suggestions": [
                        "Conduct a stakeholder workshop to define target audience",
                        "Request documentation of current system APIs for integration planning",
                        "Create a project charter to formally define scope and objectives",
                        "Schedule a budget planning meeting with finance team",
                    ],
                },
                "components": [],
            },
        }
