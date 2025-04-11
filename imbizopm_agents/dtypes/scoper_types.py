from typing import List, Literal, Union

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


class ScopeOverload(ScopeDefinitionBase):
    overload: Literal[True] = Field(
        default=True,
        description="Indicates that the scope is overloaded and needs to be reduced",
    )


ScopeDefinition = Union[NoScopeOverload, ScopeOverload]
