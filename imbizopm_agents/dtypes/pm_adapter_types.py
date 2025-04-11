from typing import Any, List, Literal

from pydantic import BaseModel, Field


class ProjectOverview(BaseModel):
    name: str = Field(description="Project name")
    description: str = Field(
        description="Brief description of the project's purpose and scope"
    )
    timeline: str = Field(
        description="Overall timeline of the project, e.g., 'Start date to end date (X weeks/months)'"
    )
    objectives: List[str] = Field(
        default_factory=list, description="List of specific project objectives"
    )
    key_stakeholders: List[str] = Field(
        default_factory=list,
        description="List of key stakeholders or roles involved in the project",
    )


class Milestone(BaseModel):
    name: str = Field(description="Name of the milestone")
    date: str = Field(description="Expected date or timeframe for the milestone")
    deliverables: List[str] = Field(
        default_factory=list,
        description="List of deliverables associated with this milestone",
    )


class ResourceRequirement(BaseModel):
    role: str = Field(
        description="Name or title of the required role (e.g., Developer, QA Analyst)"
    )
    allocation: str = Field(
        description="Level of effort or time commitment (e.g., Full-time, Part-time)"
    )
    skills: List[str] = Field(
        default_factory=list,
        description="List of essential skills required for the role",
    )


class PMToolExport(BaseModel):
    tasks: List[Any] = Field(
        default_factory=list,
        description="List of tasks for project tracking in a PM tool",
    )
    milestones: List[Any] = Field(
        default_factory=list,
        description="List of milestones formatted for PM tool import",
    )
    dependencies: List[Any] = Field(
        default_factory=list, description="List of task dependencies"
    )
    resources: List[Any] = Field(
        default_factory=list,
        description="List of resources (people, tools, etc.) linked to tasks or milestones",
    )


class ProjectSummary(BaseModel):
    executive_summary: str = Field(
        description="Concise overview of the project purpose, approach, and expected outcomes"
    )
    project_overview: ProjectOverview = Field(
        description="General overview including name, description, timeline, objectives, and stakeholders"
    )
    key_milestones: List[Milestone] = Field(
        default_factory=list,
        description="List of important project milestones with expected dates and deliverables",
    )
    resource_requirements: List[ResourceRequirement] = Field(
        default_factory=list,
        description="List of required roles, their allocations, and key skills needed for the project",
    )
    top_risks: List[Any] = Field(
        default_factory=list,
        description="List of major risks, their impact level, and mitigation strategies",
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Immediate action items or follow-up steps for the project team",
    )
    pm_tool_export: PMToolExport = Field(
        default_factory=PMToolExport,
        description="Exportable structure for project management tools including tasks, milestones, dependencies, and resources",
    )
