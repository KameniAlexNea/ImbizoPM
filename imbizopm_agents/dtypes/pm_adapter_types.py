from typing import List

from pydantic import BaseModel, Field


class ProjectOverview(BaseModel):
    name: str = Field(default="", description="Project name")
    description: str = Field(
        default="", description="Brief description of the project's purpose and scope"
    )
    timeline: str = Field(
        default="", description="Overall timeline of the project, e.g., 'Start date to end date (X weeks/months)'"
    )
    objectives: List[str] = Field(
        default_factory=list, description="List of specific project objectives"
    )
    key_stakeholders: List[str] = Field(
        default_factory=list,
        description="List of key stakeholders or roles involved in the project",
    )


class Milestone(BaseModel):
    name: str = Field(default="", description="Name of the milestone")
    date: str = Field(default="", description="Expected date or timeframe for the milestone")
    deliverables: List[str] = Field(
        default_factory=list,
        description="List of deliverables associated with this milestone",
    )


class ResourceRequirement(BaseModel):
    role: str = Field(
        default="", description="Name or title of the required role (e.g., Developer, QA Analyst)"
    )
    allocation: str = Field(
        default="", description="Level of effort or time commitment (e.g., Full-time, Part-time)"
    )
    skills: List[str] = Field(
        default_factory=list,
        description="List of essential skills required for the role",
    )


class Task(BaseModel):
    id: str = Field(default="", description="Unique identifier for the task")
    title: str = Field(default="", description="Title or name of the task")
    description: str = Field(default="", description="Detailed description of the task")
    assignees: List[str] = Field(
        default_factory=list, description="People responsible for this task"
    )
    due_date: str = Field(default="", description="Expected due date for this task")


class Dependency(BaseModel):
    from_task: str = Field(default="", description="Task ID that this task depends on")
    to_task: str = Field(default="", description="Task ID that is dependent")


class ResourceLink(BaseModel):
    name: str = Field(default="", description="Name of the resource")
    type: str = Field(default="", description="Type of the resource, e.g., tool, person")
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
    name: str = Field(default="", description="Name of the risk")
    impact: str = Field(default="", description="Impact level of the risk")
    mitigation_strategy: str = Field(default="", description="Mitigation plan for this risk")


class ProjectSummary(BaseModel):
    executive_summary: str = Field(
        default="", description="Concise overview of the project purpose, approach, and expected outcomes"
    )
    project_overview: ProjectOverview = Field(
        default_factory=ProjectOverview,
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
    top_risks: List[RiskAssessment] = Field(
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

    def to_structured_string(self) -> str:
        """Formats the project summary into a structured string."""
        output = f"**Executive Summary:**\n{self.executive_summary}\n\n"

        output += "**Project Overview:**\n"
        output += f"- **Name:** {self.project_overview.name}\n"
        output += f"- **Description:** {self.project_overview.description}\n"
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
                output += f"- **{milestone.name} ({milestone.date}):**\n"
                if milestone.deliverables:
                    for deliverable in milestone.deliverables:
                        output += f"  - {deliverable}\n"
            output += "\n"

        if self.resource_requirements:
            output += "**Resource Requirements:**\n"
            for req in self.resource_requirements:
                output += f"- **Role:** {req.role} ({req.allocation})\n"
                if req.skills:
                    output += f"  - **Skills:** {', '.join(req.skills)}\n"
            output += "\n"

        if self.top_risks:
            output += "**Top Risks:**\n"
            for risk in self.top_risks:
                output += f"- **{risk.name} (Impact: {risk.impact}):** {risk.mitigation_strategy}\n"
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
        """Return an example JSON representation of the ProjectSummary model."""
        return {
            "executive_summary": "The Customer Portal Redesign project will modernize our client-facing portal to improve user experience, increase self-service capabilities, and reduce support calls by 30%. Using agile methodology, we'll deliver a mobile-responsive, accessible platform with enhanced security features over a 6-month timeline.",
            "project_overview": {
                "name": "Customer Portal Redesign",
                "description": "Complete overhaul of the existing customer portal with modern UX/UI, expanded functionality, and improved performance",
                "timeline": "January 15, 2023 to July 15, 2023 (6 months)",
                "objectives": [
                    "Increase customer self-service adoption by 50%",
                    "Reduce support call volume by 30%",
                    "Improve customer satisfaction scores from 3.2 to 4.5 (out of 5)",
                    "Ensure WCAG 2.1 AA accessibility compliance",
                ],
                "key_stakeholders": [
                    "VP of Customer Experience",
                    "Director of IT",
                    "Customer Support Manager",
                    "UX Research Team",
                    "Customer Advisory Board",
                ],
            },
            "key_milestones": [
                {
                    "name": "Requirements & Design Approval",
                    "date": "February 28, 2023",
                    "deliverables": [
                        "Approved requirements document",
                        "Signed-off wireframes and designs",
                        "Technical architecture plan",
                    ],
                },
                {
                    "name": "Alpha Release",
                    "date": "April 30, 2023",
                    "deliverables": [
                        "Functioning prototype with core features",
                        "Internal testing results",
                        "Performance benchmarks",
                    ],
                },
                {
                    "name": "Beta Release",
                    "date": "June 15, 2023",
                    "deliverables": [
                        "Complete feature set",
                        "User acceptance testing results",
                        "Migration plan",
                    ],
                },
                {
                    "name": "Production Launch",
                    "date": "July 15, 2023",
                    "deliverables": [
                        "Fully tested production environment",
                        "Customer communication materials",
                        "Support documentation and training",
                    ],
                },
            ],
            "resource_requirements": [
                {
                    "role": "Project Manager",
                    "allocation": "Full-time",
                    "skills": [
                        "Agile methodology",
                        "Stakeholder management",
                        "Risk management",
                    ],
                },
                {
                    "role": "UX/UI Designer",
                    "allocation": "Full-time for first 3 months, part-time after",
                    "skills": [
                        "User research",
                        "Wireframing",
                        "Accessibility standards",
                        "Design systems",
                    ],
                },
                {
                    "role": "Frontend Developer",
                    "allocation": "Full-time (2 resources)",
                    "skills": [
                        "React",
                        "TypeScript",
                        "Responsive design",
                        "API integration",
                    ],
                },
                {
                    "role": "Backend Developer",
                    "allocation": "Full-time (2 resources)",
                    "skills": [
                        "Node.js",
                        "GraphQL",
                        "Database optimization",
                        "Authentication systems",
                    ],
                },
                {
                    "role": "QA Engineer",
                    "allocation": "Part-time initially, full-time during testing phases",
                    "skills": [
                        "Automated testing",
                        "Performance testing",
                        "Accessibility testing",
                    ],
                },
            ],
            "top_risks": [
                {
                    "name": "Integration with legacy systems complexity",
                    "impact": "High",
                    "mitigation_strategy": "Early technical spike to assess integration points; allocate additional buffer for integration work",
                },
                {
                    "name": "Slow user adoption due to change resistance",
                    "impact": "Medium",
                    "mitigation_strategy": "Develop comprehensive change management plan; involve customer representatives early in the process",
                },
                {
                    "name": "Security vulnerabilities in new architecture",
                    "impact": "High",
                    "mitigation_strategy": "Conduct security review at architecture phase; implement regular penetration testing",
                },
            ],
            "next_steps": [
                "Schedule kickoff meeting with all stakeholders by January 10",
                "Finalize project charter and get sign-off by January 17",
                "Begin user research interviews by January 20",
                "Set up development environment and CI/CD pipeline by January 25",
            ],
            "pm_tool_export": {
                "tasks": [
                    {
                        "id": "TASK-001",
                        "title": "User Research",
                        "description": "Conduct interviews and surveys to understand user needs for the new portal.",
                        "assignees": ["UX Team"],
                        "due_date": "2023-02-10",
                    },
                    {
                        "id": "TASK-002",
                        "title": "Wireframe Creation",
                        "description": "Develop low-fidelity wireframes based on user research.",
                        "assignees": ["UX Team"],
                        "due_date": "2023-02-25",
                    },
                    {
                        "id": "TASK-003",
                        "title": "Technical Architecture Design",
                        "description": "Define the technical stack, data models, and integration points.",
                        "assignees": ["Tech Lead"],
                        "due_date": "2023-02-20",
                    },
                ],
                "milestones": [
                    {
                        "name": "Requirements & Design Approval",
                        "date": "2023-02-28",
                        "deliverables": ["Approved requirements", "Signed-off designs"],
                    },
                    {
                        "name": "Alpha Release",
                        "date": "2023-04-30",
                        "deliverables": ["Functioning prototype"],
                    },
                    {
                        "name": "Beta Release",
                        "date": "2023-06-15",
                        "deliverables": ["Complete feature set", "UAT results"],
                    },
                    {
                        "name": "Production Launch",
                        "date": "2023-07-15",
                        "deliverables": ["Live portal", "Support docs"],
                    },
                ],
                "dependencies": [
                    {"from_task": "TASK-001", "to_task": "TASK-002"},
                    {"from_task": "TASK-002", "to_task": "MS-001"},
                    {"from_task": "TASK-003", "to_task": "MS-001"},
                ],
                "resources": [
                    {
                        "name": "John Smith (PM)",
                        "type": "person",
                        "linked_task_ids": ["TASK-001", "TASK-002", "TASK-003"],
                    },
                    {
                        "name": "UX Team",
                        "type": "team",
                        "linked_task_ids": ["TASK-001", "TASK-002"],
                    },
                    {
                        "name": "Jira",
                        "type": "tool",
                        "linked_task_ids": ["TASK-001", "TASK-002", "TASK-003"],
                    },
                ],
            },
        }
