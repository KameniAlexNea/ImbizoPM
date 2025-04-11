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
