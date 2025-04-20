from typing import List

from pydantic import BaseModel, Field


class TaskDuration(BaseModel):
    task_id: str = Field(default="", description="The unique identifier for the task")
    start: str = Field(
        default="", description='Relative start time of the task (e.g., "T+0")'
    )
    end: str = Field(
        default="", description='Relative end time of the task (e.g., "T+2")'
    )


class ProjectTimeline(BaseModel):
    task_durations: List[TaskDuration] = Field(
        default_factory=list,
        description="List of tasks with their start and end durations",
    )
    milestones: List[str] = Field(
        default_factory=list,
        description='List of key project milestones (e.g., "M1: Repo Initialized")',
    )
    critical_path: List[str] = Field(
        default_factory=list,
        description="Ordered list of task IDs forming the critical path",
    )

    def to_structured_string(self) -> str:
        """Formats the project timeline into a structured string."""
        output = "**Project Timeline:**\n\n"

        if self.task_durations:
            output += "**Task Durations (Relative):**\n"
            # Sort tasks by start time for better readability
            sorted_tasks = sorted(
                self.task_durations,
                key=lambda duration: (
                    int(duration.start.split("+")[1]) if "T+" in duration.start else 0
                ),
            )
            for duration in sorted_tasks:
                output += f"- **{duration.task_id}:** Start: {duration.start}, End: {duration.end}\n"
            output += "\n"
        else:
            output += "No task durations defined.\n\n"

        if self.milestones:
            output += "**Key Milestones:**\n"
            for milestone in self.milestones:
                output += f"- {milestone}\n"
            output += "\n"
        else:
            output += "No milestones defined.\n\n"

        if self.critical_path:
            output += "**Critical Path (Task IDs):**\n"
            output += f"- {' -> '.join(self.critical_path)}\n"
            output += "\n"
        else:
            output += "Critical path not identified.\n\n"

        return output.strip()

    @staticmethod
    def example() -> dict:
        """Return a simpler example JSON representation of the ProjectTimeline model."""
        # Assuming T represents days from project start (July 1st)
        return {
            "task_durations": [
                {"task_id": "T1", "start": "T+0", "end": "T+5"},
                {
                    "task_id": "T2",
                    "start": "T+0",
                    "end": "T+10",
                },
                {
                    "task_id": "T3",
                    "start": "T+5",
                    "end": "T+15",
                },
                {
                    "task_id": "T4",
                    "start": "T+15",
                    "end": "T+18",
                },
                {
                    "task_id": "T5",
                    "start": "T+18",
                    "end": "T+20",
                },
            ],
            "milestones": [
                "M1: Design Approved (T+5)",
                "M2: Content Received (T+10)",
                "M3: Development Complete (T+18)",
                "M4: Website Launch (T+20)",
            ],
            "critical_path": ["T1", "T3", "T4", "T5"],
        }
