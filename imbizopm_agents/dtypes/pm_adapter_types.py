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
                    "Ensure WCAG 2.1 AA accessibility compliance"
                ],
                "key_stakeholders": [
                    "VP of Customer Experience",
                    "Director of IT",
                    "Customer Support Manager",
                    "UX Research Team",
                    "Customer Advisory Board"
                ]
            },
            "key_milestones": [
                {
                    "name": "Requirements & Design Approval",
                    "date": "February 28, 2023",
                    "deliverables": [
                        "Approved requirements document",
                        "Signed-off wireframes and designs",
                        "Technical architecture plan"
                    ]
                },
                {
                    "name": "Alpha Release",
                    "date": "April 30, 2023",
                    "deliverables": [
                        "Functioning prototype with core features",
                        "Internal testing results",
                        "Performance benchmarks"
                    ]
                },
                {
                    "name": "Beta Release",
                    "date": "June 15, 2023",
                    "deliverables": [
                        "Complete feature set",
                        "User acceptance testing results",
                        "Migration plan"
                    ]
                },
                {
                    "name": "Production Launch",
                    "date": "July 15, 2023",
                    "deliverables": [
                        "Fully tested production environment",
                        "Customer communication materials",
                        "Support documentation and training"
                    ]
                }
            ],
            "resource_requirements": [
                {
                    "role": "Project Manager",
                    "allocation": "Full-time",
                    "skills": ["Agile methodology", "Stakeholder management", "Risk management"]
                },
                {
                    "role": "UX/UI Designer",
                    "allocation": "Full-time for first 3 months, part-time after",
                    "skills": ["User research", "Wireframing", "Accessibility standards", "Design systems"]
                },
                {
                    "role": "Frontend Developer",
                    "allocation": "Full-time (2 resources)",
                    "skills": ["React", "TypeScript", "Responsive design", "API integration"]
                },
                {
                    "role": "Backend Developer",
                    "allocation": "Full-time (2 resources)",
                    "skills": ["Node.js", "GraphQL", "Database optimization", "Authentication systems"]
                },
                {
                    "role": "QA Engineer",
                    "allocation": "Part-time initially, full-time during testing phases",
                    "skills": ["Automated testing", "Performance testing", "Accessibility testing"]
                }
            ],
            "top_risks": [
                {
                    "description": "Integration with legacy systems may be more complex than anticipated",
                    "impact": "High",
                    "mitigation": "Early technical spike to assess integration points; allocate additional buffer for integration work"
                },
                {
                    "description": "User adoption may be slow due to resistance to change",
                    "impact": "Medium",
                    "mitigation": "Develop comprehensive change management plan; involve customer representatives early in the process"
                },
                {
                    "description": "Security vulnerabilities in new architecture",
                    "impact": "High",
                    "mitigation": "Conduct security review at architecture phase; implement regular penetration testing"
                }
            ],
            "next_steps": [
                "Schedule kickoff meeting with all stakeholders by January 10",
                "Finalize project charter and get sign-off by January 17",
                "Begin user research interviews by January 20",
                "Set up development environment and CI/CD pipeline by January 25"
            ],
            "pm_tool_export": {
                "tasks": [
                    {"id": "TASK-001", "name": "User Research", "owner": "UX Team", "start_date": "2023-01-20", "end_date": "2023-02-10", "status": "Not Started"},
                    {"id": "TASK-002", "name": "Wireframe Creation", "owner": "UX Team", "start_date": "2023-02-11", "end_date": "2023-02-25", "status": "Not Started"},
                    {"id": "TASK-003", "name": "Technical Architecture", "owner": "Tech Lead", "start_date": "2023-02-01", "end_date": "2023-02-20", "status": "Not Started"}
                ],
                "milestones": [
                    {"id": "MS-001", "name": "Requirements & Design Approval", "date": "2023-02-28"},
                    {"id": "MS-002", "name": "Alpha Release", "date": "2023-04-30"},
                    {"id": "MS-003", "name": "Beta Release", "date": "2023-06-15"},
                    {"id": "MS-004", "name": "Production Launch", "date": "2023-07-15"}
                ],
                "dependencies": [
                    {"from": "TASK-001", "to": "TASK-002", "type": "Finish-to-Start"},
                    {"from": "TASK-002", "to": "MS-001", "type": "Finish-to-Start"},
                    {"from": "TASK-003", "to": "MS-001", "type": "Finish-to-Start"}
                ],
                "resources": [
                    {"id": "RES-001", "name": "John Smith", "role": "Project Manager", "availability": "100%"},
                    {"id": "RES-002", "name": "Sarah Jones", "role": "UX/UI Designer", "availability": "100%"},
                    {"id": "RES-003", "name": "Michael Lee", "role": "Frontend Developer", "availability": "100%"}
                ]
            }
        }
