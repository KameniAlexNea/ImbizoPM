from typing import List, Optional

from pydantic import BaseModel, Field


class Task(BaseModel):
    id: str = Field(
        default="", description="Unique identifier for the task"
    )  # Added default
    name: str = Field(
        default="", description="Brief, descriptive name of the task"
    )  # Added default
    description: str = Field(
        default="",  # Added default
        description="Detailed description of what needs to be done",
    )
    deliverable: Optional[str] = Field(
        description="Specific deliverable this task contributes to"
    )
    owner_role: str = Field(
        default="", description="Role responsible for completing this task"
    )  # Added default
    estimated_effort: str = Field(
        default="Medium",  # Added default
        description="Estimated effort required to complete this task. (Low, Medium, High)",
    )
    epic: Optional[str] = Field(description="Name of the epic this task belongs to")
    phase: Optional[str] = Field(
        description="Phase in which this task is to be executed"
    )
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


class TaskPlan(BaseModel):
    missing_info_details: Optional[MissingInfoDetails] = Field(
        default=None,
        description="Details about what information is missing and how to address it",
    )
    missing_info: Optional[bool] = Field(
        default=False,
        description="Flag indicating that important task-related information is missing",
    )
    tasks: List[Task] = Field(
        default_factory=list,
        description="List of defined tasks",
    )

    def to_structured_string(self) -> str:
        """Formats the task plan into a structured string."""
        if self.missing_info and self.missing_info_details:
            output = "**Task Plan Status: Missing Information**\n\n"
            output += "Cannot define tasks due to missing information. Please address the following:\n\n"

            if self.missing_info_details.unclear_aspects:
                output += "**Unclear Aspects:**\n"
                for aspect in self.missing_info_details.unclear_aspects:
                    output += f"- {aspect}\n"
                output += "\n"

            if self.missing_info_details.questions:
                output += "**Questions to Address:**\n"
                for question in self.missing_info_details.questions:
                    output += f"- {question}\n"
                output += "\n"

            if self.missing_info_details.suggestions:
                output += "**Suggestions for Clarification:**\n"
                for suggestion in self.missing_info_details.suggestions:
                    output += f"- {suggestion}\n"
                output += "\n"
        elif not self.tasks:
            output = "**Task Plan:**\n\nNo tasks defined.\n"
        else:
            output = "**Task Plan:**\n\n"
            for task in self.tasks:
                output += f"**Task ID:** {task.id}\n"
                output += f"- **Name:** {task.name}\n"
                output += f"- **Description:** {task.description}\n"
                if task.deliverable:
                    output += f"- **Deliverable:** {task.deliverable}\n"
                output += f"- **Owner Role:** {task.owner_role}\n"
                output += f"- **Estimated Effort:** {task.estimated_effort}\n"
                if task.epic:
                    output += f"- **Epic:** {task.epic}\n"
                if task.phase:
                    output += f"- **Phase:** {task.phase}\n"
                if task.dependencies:
                    output += f"- **Dependencies:** {', '.join(task.dependencies)}\n"
                else:
                    output += "- **Dependencies:** None\n"
                output += "\n"

        return output.strip()

    @staticmethod
    def example() -> dict:
        """Return simpler examples of both a complete and missing info task plan."""
        return {
            "complete_plan": {
                "tasks": [
                    {
                        "id": "T1",
                        "name": "Design Website Mock-up",
                        "description": "Create a visual design concept for the bakery website.",
                        "deliverable": "Website Mock-up",
                        "owner_role": "Web Designer",
                        "estimated_effort": "Low",
                        "epic": "Website Visuals",
                        "phase": "Phase 1: Launch Basic Site",
                        "dependencies": [],
                    },
                    {
                        "id": "T2",
                        "name": "Gather Menu Content",
                        "description": "Collect text and images for the menu page from the bakery owner.",
                        "deliverable": "Menu Content",
                        "owner_role": "Bakery Owner",
                        "estimated_effort": "Low",
                        "epic": "Website Content",
                        "phase": "Phase 1: Launch Basic Site",
                        "dependencies": [],
                    },
                    {
                        "id": "T3",
                        "name": "Develop HTML/CSS Structure",
                        "description": "Build the basic HTML structure and apply CSS styling based on the approved design.",
                        "deliverable": "Website Codebase",
                        "owner_role": "Web Developer",
                        "estimated_effort": "Medium",
                        "epic": "Website Development",
                        "phase": "Phase 1: Launch Basic Site",
                        "dependencies": ["T1", "T2"],
                    },
                    {
                        "id": "T4",
                        "name": "Implement Mobile Responsiveness",
                        "description": "Ensure the website layout adapts correctly to different screen sizes (mobile, tablet, desktop).",
                        "deliverable": "Responsive Website Code",
                        "owner_role": "Web Developer",
                        "estimated_effort": "Low",
                        "epic": "Website Development",
                        "phase": "Phase 1: Launch Basic Site",
                        "dependencies": ["T3"],
                    },
                    {
                        "id": "T5",
                        "name": "Deploy Website",
                        "description": "Upload website files to the hosting server and configure the domain name.",
                        "deliverable": "Live Website",
                        "owner_role": "Web Developer",
                        "estimated_effort": "Low",
                        "epic": "Website Deployment",
                        "phase": "Phase 1: Launch Basic Site",
                        "dependencies": ["T4"],
                    },
                ],
                "missing_info": False,
                "missing_info_details": None,
            },
            "missing_plan": {
                "missing_info": True,
                "missing_info_details": {
                    "unclear_aspects": [
                        "Specific hosting provider is not chosen.",
                        "Domain name registration details are missing.",
                        "Final approval process for the design is unclear.",
                    ],
                    "questions": [
                        "Which hosting provider should be used?",
                        "Has the domain name been purchased? If so, what are the login details?",
                        "Who gives the final sign-off on the website design?",
                    ],
                    "suggestions": [
                        "Research and select a hosting provider based on budget and needs.",
                        "Confirm domain name status and obtain necessary credentials.",
                        "Define a clear design approval step with the bakery owner.",
                    ],
                },
                "tasks": [],
            },
        }
