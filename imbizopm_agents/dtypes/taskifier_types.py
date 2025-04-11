from typing import Any, List, Literal, Union

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
    dependencies: List[str] = Field(
        default_factory=list, description="List of task IDs this task depends on"
    )


class MissingInfoDetails(BaseModel):
    unclear_aspects: List[str] = Field(
        default_factory=list,
        description="Key points that are unclear and block task definition",
    )
    questions: List[str] = Field(
        default_factory=list,
        description="Questions that must be answered to clarify the scope",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Concrete suggestions to resolve ambiguity or missing details",
    )


class TaskPlanComplete(BaseModel):
    tasks: List[Task] = Field(
        default_factory=list, description="List of well-defined tasks"
    )
    missing_info: Literal[False] = Field(
        default=False,
        description="Flag indicating that no critical information is missing",
    )
    missing_info_details: MissingInfoDetails = Field(
        default_factory=MissingInfoDetails,
        description="Empty structure when no info is missing",
    )


class TaskPlanMissingInfo(BaseModel):
    missing_info_details: MissingInfoDetails = Field(
        description="Details about what information is missing and how to address it"
    )
    missing_info: Literal[True] = Field(
        default=True,
        description="Flag indicating that important task-related information is missing",
    )
    tasks: List[Task] = Field(
        default_factory=list,
        description="Empty list since tasks can't be defined without resolving issues",
    )


TaskPlan = Union[TaskPlanComplete, TaskPlanMissingInfo]
