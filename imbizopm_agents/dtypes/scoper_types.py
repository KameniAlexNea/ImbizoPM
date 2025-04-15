from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MVPItem(BaseModel):
    feature: str = Field(default="", description="A specific feature included in the MVP.")
    user_story: Optional[str] = Field(
        None,
        description="User story for the feature (e.g., 'As a [user type], I want [capability] so that [benefit]').",
    )


class Phase(BaseModel):
    name: str = Field(default="", description="Name of the phase (e.g., MVP, Phase 2)")
    description: str = Field(
        default="",
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


class ScopeDefinition(BaseModel):
    mvp: List[MVPItem] = Field(
        default_factory=list,
        description="List of Minimum Viable Product features and their corresponding user stories."
    )
    exclusions: Optional[List[str]] = Field(
        default_factory=list,
        description="List of features or functionalities explicitly excluded from the scope.",
    )
    phases: Optional[List[Phase]] = Field(
        default_factory=list,
        description="Optional breakdown of the project into phases.",
    )
    overload: Optional[OverloadDetails] = Field(
        description="Details if the scope is considered overloaded, otherwise None.",
    )

    def to_structured_string(self) -> str:
        """Formats the scope definition into a structured string."""
        if self.overload:
            output = "**Scope Status: Overloaded**\n\n"
            output += "The proposed scope exceeds feasible limits. Please review the following:\n\n"

            if self.overload.problem_areas:
                output += "**Problem Areas:**\n"
                for area in self.overload.problem_areas:
                    output += f"- {area}\n"
                output += "\n"

            if self.overload.recommendations:
                output += "**Recommendations for Scope Reduction:**\n"
                for rec in self.overload.recommendations:
                    output += f"- {rec}\n"
                output += "\n"
        else:
            output = "**Scope Definition:**\n\n"

            if self.mvp:
                output += "**Minimum Viable Product (MVP):**\n"
                for item in self.mvp:
                    user_story_text = f" ({item.user_story})" if item.user_story else ""
                    output += f"- **Feature:** {item.feature}{user_story_text}\n"
                output += "\n"

            if self.exclusions:
                output += "**Exclusions (Out of Scope):**\n"
                for exclusion in self.exclusions:
                    output += f"- {exclusion}\n"
                output += "\n"

            if self.phases:
                output += "**Project Phases:**\n"
                for phase in self.phases:
                    output += f"- **{phase.name}:** {phase.description}\n"
                output += "\n"

        return output.strip()

    @staticmethod
    def example() -> Dict[str, Any]:
        """Return examples of both manageable and overloaded scope definitions."""
        return {
            "manageable_scope": {
                "mvp": [
                    {
                        "feature": "User authentication and account management",
                        "user_story": "As a customer, I want to create an account so that I can access personalized features",
                    },
                    {
                        "feature": "Basic dashboard with key performance metrics",
                        "user_story": "As a manager, I want to view key metrics at a glance so that I can make informed decisions quickly",
                    },
                    {
                        "feature": "Search functionality for main content types",
                        "user_story": "As a user, I want to search for content by keyword so that I can find relevant information efficiently",
                    },
                    {
                        "feature": "Notification system for status updates",
                        "user_story": "As a team member, I want to receive notifications when tasks are assigned to me so that I can prioritize my work",
                    },
                ],
                "exclusions": [
                    "Advanced analytics and reporting features",
                    "Integration with third-party platforms",
                    "Mobile application (web responsive only for MVP)",
                    "Real-time collaboration tools",
                ],
                "phases": [
                    {
                        "name": "MVP",
                        "description": "Core functionality focused on user authentication, basic dashboard, search, and notifications",
                    },
                    {
                        "name": "Phase 2",
                        "description": "Enhanced analytics, reporting capabilities, and initial third-party integrations",
                    },
                    {
                        "name": "Phase 3",
                        "description": "Mobile application development and advanced collaboration features",
                    },
                ],
                "overload": None,
            },
            "overloaded_scope": {
                "mvp": [
                    {
                        "feature": "User Authentication",
                        "user_story": "As a user, I want to log in securely.",
                    },
                    {
                        "feature": "Core Data Entry",
                        "user_story": "As an admin, I want to input basic data.",
                    },
                ],
                "exclusions": None,
                "phases": None,
                "overload": {
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
            },
        }
