from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectOverview(BaseModel):
    name: Optional[str] = Field(default=None, description="Project name")
    description: Optional[str] = Field(
        default=None, description="Brief description of the project's purpose and scope"
    )
    timeline: Optional[str] = Field(
        default=None,
        description="Overall timeline of the project, e.g., 'Start date to end date (X weeks/months)'",
    )
    objectives: List[str] = Field(
        default_factory=list, description="List of specific project objectives"
    )
    key_stakeholders: List[str] = Field(
        default_factory=list,
        description="List of key stakeholders or roles involved in the project",
    )


class Milestone(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the milestone")
    date: Optional[str] = Field(
        default=None, description="Expected date or timeframe for the milestone"
    )
    deliverables: List[str] = Field(
        default_factory=list,
        description="List of deliverables associated with this milestone",
    )


class ResourceRequirement(BaseModel):
    role: Optional[str] = Field(
        default=None,
        description="Name or title of the required role (e.g., Developer, QA Analyst)",
    )
    allocation: Optional[str] = Field(
        default=None,
        description="Level of effort or time commitment (e.g., Full-time, Part-time)",
    )
    skills: List[str] = Field(
        default_factory=list,
        description="List of essential skills required for the role",
    )


class Task(BaseModel):
    id: Optional[str] = Field(
        default=None, description="Unique identifier for the task"
    )
    title: Optional[str] = Field(default=None, description="Title or name of the task")
    description: Optional[str] = Field(
        default=None, description="Detailed description of the task"
    )
    assignees: List[str] = Field(
        default_factory=list, description="People responsible for this task"
    )
    due_date: Optional[str] = Field(
        default=None, description="Expected due date for this task"
    )


class Dependency(BaseModel):
    from_task: Optional[str] = Field(
        default=None, description="Task ID that this task depends on"
    )
    to_task: Optional[str] = Field(
        default=None, description="Task ID that is dependent"
    )


class ResourceLink(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the resource")
    type: Optional[str] = Field(
        default=None, description="Type of the resource, e.g., tool, person"
    )
    linked_task_ids: List[str] = Field(
        default_factory=list,
        description="IDs of tasks/milestones associated with this resource",
    )


class PMToolExport(BaseModel):
    tasks: List[Task] = Field(
        default_factory=list,
        description="List of tasks for project tracking in a PM tool",
    )
    milestones: List[Milestone] = Field(
        default_factory=list,
        description="List of milestones formatted for PM tool import",
    )
    dependencies: List[Dependency] = Field(
        default_factory=list, description="List of task dependencies"
    )
    resources: List[ResourceLink] = Field(
        default_factory=list,
        description="List of resources (people, tools, etc.) linked to tasks or milestones",
    )


class RiskAssessment(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the risk")
    impact: Optional[str] = Field(default=None, description="Impact level of the risk")
    mitigation_strategy: Optional[str] = Field(
        default=None, description="Mitigation plan for this risk"
    )


class ProjectSummary(BaseModel):
    executive_summary: Optional[str] = Field(
        default=None,
        description="Concise overview of the project purpose, approach, and expected outcomes",
    )
    project_overview: Optional[ProjectOverview] = Field(
        default_factory=ProjectOverview,
        description="General overview including name, description, timeline, objectives, and stakeholders",
    )
    key_milestones: List[Milestone] = Field(
        default_factory=list,
        description="List of important project milestones with expected dates and deliverables",
    )
    resource_requirements: List[ResourceRequirement] = Field(
        default_factory=list,
        description="List of required roles, their allocations, and key skills needed for the project",
    )
    top_risks: List[RiskAssessment] = Field(
        default_factory=list,
        description="List of major risks, their impact level, and mitigation strategies",
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Immediate action items or follow-up steps for the project team",
    )
    pm_tool_export: Optional[PMToolExport] = Field(
        default_factory=PMToolExport,
        description="Exportable structure for project management tools including tasks, milestones, dependencies, and resources",
    )

    def to_structured_string(self) -> str:
        """Formats the project summary into a structured string."""
        output = ""
        if self.executive_summary:
            output += f"**Executive Summary:**\n{self.executive_summary}\n\n"

        if self.project_overview:
            output += "**Project Overview:**\n"
            if self.project_overview.name:
                output += f"- **Name:** {self.project_overview.name}\n"
            if self.project_overview.description:
                output += f"- **Description:** {self.project_overview.description}\n"
            if self.project_overview.timeline:
                output += f"- **Timeline:** {self.project_overview.timeline}\n"
            if self.project_overview.objectives:
                output += "- **Objectives:**\n"
                for objective in self.project_overview.objectives:
                    output += f"  - {objective}\n"
            if self.project_overview.key_stakeholders:
                output += "- **Key Stakeholders:**\n"
                for stakeholder in self.project_overview.key_stakeholders:
                    output += f"  - {stakeholder}\n"
            output += "\n"

        if self.key_milestones:
            output += "**Key Milestones:**\n"
            for milestone in self.key_milestones:
                name = milestone.name or "Unnamed Milestone"
                date = f" ({milestone.date})" if milestone.date else ""
                output += f"- **{name}{date}:**\n"
                if milestone.deliverables:
                    for deliverable in milestone.deliverables:
                        output += f"  - {deliverable}\n"
            output += "\n"

        if self.resource_requirements:
            output += "**Resource Requirements:**\n"
            for req in self.resource_requirements:
                role = req.role or "Unnamed Role"
                allocation = f" ({req.allocation})" if req.allocation else ""
                output += f"- **Role:** {role}{allocation}\n"
                if req.skills:
                    output += f"  - **Skills:** {', '.join(req.skills)}\n"
            output += "\n"

        if self.top_risks:
            output += "**Top Risks:**\n"
            for risk in self.top_risks:
                name = risk.name or "Unnamed Risk"
                impact = f" (Impact: {risk.impact})" if risk.impact else ""
                strategy = risk.mitigation_strategy or "No strategy defined"
                output += f"- **{name}{impact}:** {strategy}\n"
            output += "\n"

        if self.next_steps:
            output += "**Next Steps:**\n"
            for step in self.next_steps:
                output += f"- {step}\n"
            output += "\n"

        # Note: pm_tool_export is intentionally omitted for brevity in the summary string.

        return output.strip()

    @staticmethod
    def example() -> dict:
        """Return a simpler example JSON representation of the ProjectSummary model."""
        return {
            "executive_summary": "Develop a basic website for a local bakery to display their menu and contact information. The project aims to establish an online presence within 4 weeks and a budget of $1000.",
            "project_overview": {
                "name": "Bakery Website Launch",
                "description": "Create a simple, informational website for a local bakery.",
                "timeline": "July 1, 2024 to July 28, 2024 (4 weeks)",
                "objectives": [
                    "Launch a live website with menu and contact info.",
                    "Ensure the website is mobile-friendly.",
                    "Stay within the $1000 budget.",
                ],
                "key_stakeholders": ["Bakery Owner", "Web Developer"],
            },
            "key_milestones": [
                {
                    "name": "Design Approval",
                    "date": "July 8, 2024",
                    "deliverables": ["Website mock-up approved"],
                },
                {
                    "name": "Content Finalized",
                    "date": "July 15, 2024",
                    "deliverables": ["Menu text and images provided"],
                },
                {
                    "name": "Website Launch",
                    "date": "July 28, 2024",
                    "deliverables": ["Live website accessible online"],
                },
            ],
            "resource_requirements": [
                {
                    "role": "Web Developer",
                    "allocation": "Part-time (approx. 20 hours/week)",
                    "skills": ["HTML", "CSS", "Basic JavaScript", "Web Hosting"],
                },
                {
                    "role": "Content Provider (Bakery Owner)",
                    "allocation": "As needed",
                    "skills": ["Knowledge of bakery products"],
                },
            ],
            "top_risks": [
                {
                    "name": "Delay in receiving content",
                    "impact": "Medium",
                    "mitigation_strategy": "Set clear deadlines for content delivery; have placeholder content ready.",
                },
                {
                    "name": "Scope creep (requests for extra features)",
                    "impact": "Medium",
                    "mitigation_strategy": "Clearly define scope in initial agreement; use change request process for new features.",
                },
            ],
            "next_steps": [
                "Finalize contract with Web Developer.",
                "Schedule initial meeting to discuss design preferences.",
                "Gather initial content (logo, contact details).",
            ],
            "pm_tool_export": {
                "tasks": [
                    {
                        "id": "T1",
                        "title": "Design Mock-up",
                        "description": "Create visual design for the website.",
                        "assignees": ["Web Developer"],
                        "due_date": "2024-07-07",
                    },
                    {
                        "id": "T2",
                        "title": "Gather Content",
                        "description": "Collect menu details, photos, and text from owner.",
                        "assignees": ["Bakery Owner"],
                        "due_date": "2024-07-14",
                    },
                    {
                        "id": "T3",
                        "title": "Develop Website",
                        "description": "Build the website based on design and content.",
                        "assignees": ["Web Developer"],
                        "due_date": "2024-07-26",
                    },
                    {
                        "id": "T4",
                        "title": "Deploy Website",
                        "description": "Publish the website to a live server.",
                        "assignees": ["Web Developer"],
                        "due_date": "2024-07-28",
                    },
                ],
                "milestones": [
                    {
                        "name": "Design Approval",
                        "date": "2024-07-08",
                        "deliverables": ["Mock-up approved"],
                    },
                    {
                        "name": "Website Launch",
                        "date": "2024-07-28",
                        "deliverables": ["Live website"],
                    },
                ],
                "dependencies": [
                    {"from_task": "T1", "to_task": "T3"},
                    {"from_task": "T2", "to_task": "T3"},
                    {"from_task": "T3", "to_task": "T4"},
                ],
                "resources": [
                    {
                        "name": "Web Developer",
                        "type": "person",
                        "linked_task_ids": ["T1", "T3", "T4"],
                    },
                    {
                        "name": "Bakery Owner",
                        "type": "person",
                        "linked_task_ids": ["T2"],
                    },
                ],
            },
        }
