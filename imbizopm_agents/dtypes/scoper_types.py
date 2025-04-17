from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MVPItem(BaseModel):
    feature: str = Field(
        default="", description="A specific feature included in the MVP."
    )
    user_story: Optional[str] = Field(
        None,
        description="User story for the feature (e.g., 'As a [user type], I want [capability] so that [benefit]').",
    )


class Phase(BaseModel):
    name: str = Field(default="", description="Name of the project phase.")
    features: List[str] = Field(
        default_factory=list,
        description="List of features included in this project phase.",
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
        description="List of Minimum Viable Product features and their corresponding user stories.",
    )
    exclusions: Optional[List[str]] = Field(
        default_factory=list,
        description="List of features or functionalities explicitly excluded from the scope.",
    )
    phases: Optional[List[Phase]] = Field(
        default_factory=list,
        description="Optional breakdown of the project into phases, each with a name and a list of features.",
    )
    overload: Optional[OverloadDetails] = Field(
        default=None,
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
                    output += f"- **{phase.name}:**\n"
                    for feature in phase.features:
                        output += f"  - {feature}\n"
                output += "\n"

        return output.strip()

    @staticmethod
    def example() -> Dict[str, Any]:
        """Return simpler examples of both manageable and overloaded scope definitions."""
        return {
            "manageable_scope": {
                "mvp": [
                    {
                        "feature": "Display Menu Page",
                        "user_story": "As a customer, I want to see the bakery's menu online so I know what they offer.",
                    },
                    {
                        "feature": "Display Contact Information",
                        "user_story": "As a customer, I want to find the bakery's address and phone number easily.",
                    },
                    {
                        "feature": "Mobile Responsiveness",
                        "user_story": "As a customer, I want the website to look good on my phone.",
                    },
                ],
                "exclusions": [
                    "Online ordering system",
                    "User accounts or login",
                    "Blog or news section",
                    "Photo gallery (beyond menu items)",
                ],
                "phases": [
                    {
                        "name": "Phase 1: Launch Basic Site",
                        "features": [
                            "Display Menu Page",
                            "Display Contact Information",
                            "Mobile Responsiveness",
                        ],
                    },
                    {
                        "name": "Phase 2: Potential Enhancements (Future)",
                        "features": ["Online ordering system", "Photo gallery"],
                    },
                ],
                "overload": None,
            },
            "overloaded_scope": {
                "mvp": [
                    {"feature": "Display Menu"},
                    {"feature": "Contact Form"},
                    {"feature": "Online Ordering"},
                    {"feature": "User Accounts"},
                    {"feature": "Blog"},
                    {"feature": "Admin Dashboard"},
                ],
                "exclusions": None,
                "phases": None,
                "overload": {
                    "problem_areas": [
                        "Online ordering and user accounts add significant complexity.",
                        "Blog requires ongoing content creation effort.",
                        "Scope exceeds the typical budget/timeline for a simple bakery site.",
                    ],
                    "recommendations": [
                        "Focus MVP on Menu, Contact Info, and Mobile Responsiveness.",
                        "Defer online ordering, user accounts, and blog to future phases.",
                        "Re-evaluate budget and timeline if advanced features are critical for launch.",
                    ],
                },
            },
        }
