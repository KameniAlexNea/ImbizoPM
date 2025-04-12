from typing import Any, Dict, List, Literal, Union

from pydantic import BaseModel, Field


class MVPScope(BaseModel):
    features: List[str] = Field(
        default_factory=list,
        description="List of essential features that must be included in the MVP",
    )
    user_stories: List[str] = Field(
        default_factory=list,
        description="List of user stories in the format: 'As a [user type], I want [capability] so that [benefit]'",
    )


class Phase(BaseModel):
    phase: str = Field(description="Name of the phase (e.g., MVP, Phase 2)")
    description: str = Field(
        description="Detailed description of this phase's focus and activities"
    )


class OverloadDetails(BaseModel):
    problem_areas: List[str] = Field(
        default_factory=list,
        description="Specific areas where the scope is too ambitious or exceeds resource constraints",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommended actions or trade-offs to reduce scope to a feasible level",
    )


class ScopeDefinitionBase(BaseModel):
    mvp_scope: MVPScope = Field(description="Core MVP features and user stories")
    scope_exclusions: List[str] = Field(
        default_factory=list,
        description="Capabilities explicitly excluded from MVP to maintain focus",
    )
    phased_approach: List[Phase] = Field(
        default_factory=list,
        description="Phases for delivering additional capabilities beyond MVP",
    )
    overload_details: OverloadDetails = Field(
        default_factory=OverloadDetails,
        description="Detailed explanation of any scope overload issues and suggestions",
    )


class NoScopeOverload(ScopeDefinitionBase):
    overload: Literal[False] = Field(
        default=False,
        description="Indicates that the current MVP scope is feasible without overload",
    )

    @staticmethod
    def example() -> dict:
        """Return an example JSON representation of a scope definition without overload."""
        return {
            "overload": False,
            "mvp_scope": {
                "features": [
                    "User authentication and account management",
                    "Basic dashboard with key performance metrics",
                    "Search functionality for main content types",
                    "Notification system for status updates",
                ],
                "user_stories": [
                    "As a customer, I want to create an account so that I can access personalized features",
                    "As a manager, I want to view key metrics at a glance so that I can make informed decisions quickly",
                    "As a user, I want to search for content by keyword so that I can find relevant information efficiently",
                    "As a team member, I want to receive notifications when tasks are assigned to me so that I can prioritize my work",
                ],
            },
            "scope_exclusions": [
                "Advanced analytics and reporting features",
                "Integration with third-party platforms",
                "Mobile application (web responsive only for MVP)",
                "Real-time collaboration tools",
            ],
            "phased_approach": [
                {
                    "phase": "MVP",
                    "description": "Core functionality focused on user authentication, basic dashboard, search, and notifications",
                },
                {
                    "phase": "Phase 2",
                    "description": "Enhanced analytics, reporting capabilities, and initial third-party integrations",
                },
                {
                    "phase": "Phase 3",
                    "description": "Mobile application development and advanced collaboration features",
                },
            ],
            "overload_details": {"problem_areas": [], "recommendations": []},
        }


class ScopeOverload(ScopeDefinitionBase):
    overload: Literal[True] = Field(
        default=True,
        description="Indicates that the scope is overloaded and needs to be reduced",
    )

    @staticmethod
    def example() -> dict:
        """Return an example JSON representation of a scope definition with overload."""
        return {
            "overload": True,
            "mvp_scope": {
                "features": [
                    "User authentication and account management",
                    "Comprehensive dashboard with real-time analytics",
                    "Advanced search with filtering and sorting capabilities",
                    "Notification system with customizable alerts",
                    "Document management with version control",
                    "Integration with CRM and ERP systems",
                    "Mobile applications for iOS and Android",
                ],
                "user_stories": [
                    "As a customer, I want to create an account so that I can access personalized features",
                    "As a manager, I want to view detailed real-time analytics so that I can track performance continuously",
                    "As a user, I want advanced search capabilities so that I can find precisely what I need",
                    "As a team member, I want customizable notifications so that I can control what updates I receive",
                    "As a content creator, I want document version control so that I can track changes over time",
                    "As a sales rep, I want CRM integration so that I can access customer data without switching applications",
                    "As a mobile user, I want a native app so that I can work efficiently on my smartphone",
                ],
            },
            "scope_exclusions": [
                "AI-powered recommendations",
                "White-labeling capabilities",
            ],
            "phased_approach": [
                {
                    "phase": "MVP",
                    "description": "Too many features currently included in MVP scope",
                },
                {
                    "phase": "Phase 2",
                    "description": "Features to be determined after MVP scope reduction",
                },
            ],
            "overload_details": {
                "problem_areas": [
                    "Too many features planned for the MVP given timeline and resources",
                    "Mobile application development requires specialized skills not currently available",
                    "Integration with multiple systems significantly increases complexity and testing requirements",
                    "Real-time analytics requires substantial backend infrastructure not accounted for in initial planning",
                ],
                "recommendations": [
                    "Reduce MVP to core authentication, basic dashboard, simple search, and essential notifications only",
                    "Move all integrations to Phase 2 to reduce initial complexity",
                    "Develop responsive web application first and defer native mobile apps to Phase 3",
                    "Simplify analytics to basic reporting in MVP and add real-time capabilities in later phases",
                ],
            },
        }


class ScopeDefinition(BaseModel):
    result: Union[NoScopeOverload, ScopeOverload]

    @staticmethod
    def example() -> Dict[str, Any]:
        """Return examples of both no overload and overloaded scope definitions."""
        return {
            "no_overload_example": NoScopeOverload.example(),
            "overload_example": ScopeOverload.example(),
        }
