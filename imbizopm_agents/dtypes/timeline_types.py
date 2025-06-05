from typing import List, Optional

from pydantic import BaseModel, Field


class MissingInformationDetails(BaseModel):
    unclear_aspects: List[str] = Field(
        default_factory=list,
        description="Specific timeline aspects that cannot be determined from available information",
    )
    questions: List[str] = Field(
        default_factory=list,
        description="Questions that need answers to create a proper timeline",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for how to provide the needed information",
    )
    source: Optional[str] = Field(
        default=None,
        description="Identifies the likely source of the missing information: 'tasks', 'dependencies', 'resources', or other",
    )


class Milestone(BaseModel):
    name: str = Field(default="", description="Name of the milestone")
    time_point: str = Field(
        default="",
        description="Relative time point of the milestone (e.g., 'T0+2w' for 2 weeks after start)",
    )
    description: Optional[str] = Field(
        default=None, description="Description of what this milestone represents"
    )


class ScheduledTask(BaseModel):
    task_id: str = Field(default="", description="ID of the task")
    start_point: str = Field(
        default="", description="Relative start time point (e.g., 'T0', 'T0+2w')"
    )
    end_point: str = Field(
        default="", description="Relative end time point (e.g., 'T0+1w', 'T0+3w')"
    )
    duration: str = Field(
        default="", description="Duration estimate (e.g., '3 days', '1 week')"
    )
    dependencies_satisfied: bool = Field(
        default=True,
        description="Whether all dependencies are satisfied by this schedule",
    )


class ProjectTimeline(BaseModel):
    information_missing: bool = Field(
        default=False,
        description="Whether critical information needed for timeline creation is missing",
    )
    missing_information_details: Optional[MissingInformationDetails] = Field(
        default=None,
        description="Details about missing information (if information_missing is true)",
    )
    estimated_duration: Optional[str] = Field(
        default=None, description="Overall estimated project duration (e.g., '3 weeks')"
    )
    start_point: Optional[str] = Field(
        default="T0", description="Project start reference point, typically 'T0'"
    )
    end_point: Optional[str] = Field(
        default=None,
        description="Relative project end point (e.g., 'T0+12w' for 12 weeks after start)",
    )
    milestones: List[Milestone] = Field(
        default_factory=list, description="List of project milestones"
    )
    scheduled_tasks: List[ScheduledTask] = Field(
        default_factory=list,
        description="List of scheduled tasks with timing information",
    )
    critical_path: List[str] = Field(
        default_factory=list,
        description="List of task IDs that form the critical path of the project",
    )
    risks: List[str] = Field(
        default_factory=list, description="List of identified timeline-related risks"
    )

    def is_valid(self) -> bool:
        """Check if the timeline is valid."""
        return not self.information_missing and self.scheduled_tasks

    @staticmethod
    def example() -> dict:
        """Return examples of both complete and incomplete timeline data."""
        return {
            "complete_timeline": {
                "information_missing": False,
                "estimated_duration": "3 weeks",
                "start_point": "T0",
                "end_point": "T0+3w",
                "milestones": [
                    {
                        "name": "Design Approval",
                        "time_point": "T0+1w",
                        "description": "Client approval",
                    }
                ],
                "scheduled_tasks": [
                    {
                        "task_id": "T1",
                        "start_point": "T0",
                        "end_point": "T0+5d",
                        "duration": "5 days",
                        "dependencies_satisfied": True,
                    },
                    {
                        "task_id": "T2",
                        "start_point": "T0+6d",
                        "end_point": "T0+10d",
                        "duration": "5 days",
                        "dependencies_satisfied": True,
                    },
                ],
                "critical_path": ["T1", "T2"],
                "risks": ["Potential delay in design approval"],
            },
            "missing_timeline": {
                "information_missing": True,
                "missing_information_details": {
                    "unclear_aspects": ["Task dependencies are ambiguous"],
                    "questions": ["What is the logical sequence between tasks?"],
                    "suggestions": ["Clarify the dependencies between tasks"],
                    "source": "tasks",
                },
                "start_point": "T0",
                "milestones": [],
                "scheduled_tasks": [],
                "critical_path": [],
                "risks": [],
            },
        }
