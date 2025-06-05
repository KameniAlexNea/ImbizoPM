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
    source: Optional[str] = Field(
        default=None,
        description="Identifies the likely source of the missing information: 'scope', 'plan', 'requirements', or other",
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

    def is_valid(self) -> bool:
        """Check if the task plan is valid."""
        return (
            not self.missing_info
            or self.tasks is None
            and not self.missing_info_details.unclear_aspects
        )

    def to_structured_string(self) -> str:
        """Formats the task plan into a structured string."""
        if not self.is_valid():
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
                        "description": "Create a visual design concept",
                        "deliverable": "Website Mock-up",
                        "owner_role": "Web Designer",
                        "estimated_effort": "Low",
                        "epic": "Website Visuals",
                        "phase": "Phase 1",
                        "dependencies": [],
                    },
                    {
                        "id": "T2",
                        "name": "Develop HTML/CSS",
                        "description": "Build the basic structure",
                        "deliverable": "Website Code",
                        "owner_role": "Developer",
                        "estimated_effort": "Medium",
                        "epic": "Development",
                        "phase": "Phase 1",
                        "dependencies": ["T1"],
                    },
                ],
                "missing_info": False,
                "missing_info_details": None,
            },
            "missing_plan": {
                "missing_info": True,
                "missing_info_details": {
                    "unclear_aspects": ["Hosting details missing"],
                    "questions": ["Which hosting provider?"],
                    "suggestions": ["Select a hosting provider"],
                    "source": "requirements",
                },
                "tasks": [],
            },
        }
