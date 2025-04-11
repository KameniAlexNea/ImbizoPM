from typing import Dict, List

from pydantic import BaseModel, Field


class TaskDuration(BaseModel):
    start: str = Field(description='Relative start time of the task (e.g., "T+0")')
    end: str = Field(description='Relative end time of the task (e.g., "T+2")')


class ProjectTimeline(BaseModel):
    task_durations: Dict[str, TaskDuration] = Field(
        default_factory=dict,
        description="Mapping from task ID to its start and end durations",
    )
    milestones: List[str] = Field(
        default_factory=list,
        description='List of key project milestones (e.g., "M1: Repo Initialized")',
    )
    critical_path: List[str] = Field(
        default_factory=list,
        description="Ordered list of task IDs forming the critical path",
    )
    
    @staticmethod
    def example() -> dict:
        """Return an example JSON representation of the ProjectTimeline model."""
        return {
            "task_durations": {
                "TASK-001": {
                    "start": "T+0",
                    "end": "T+5"
                },
                "TASK-002": {
                    "start": "T+0",
                    "end": "T+3"
                },
                "TASK-003": {
                    "start": "T+3",
                    "end": "T+8"
                },
                "TASK-004": {
                    "start": "T+5",
                    "end": "T+10"
                },
                "TASK-005": {
                    "start": "T+8",
                    "end": "T+12"
                },
                "TASK-006": {
                    "start": "T+10",
                    "end": "T+15"
                }
            },
            "milestones": [
                "M1: Project Kickoff (T+0)",
                "M2: Requirements Finalized (T+5)",
                "M3: Design Complete (T+10)",
                "M4: Development Complete (T+15)",
                "M5: Testing Complete (T+20)",
                "M6: Project Launch (T+22)"
            ],
            "critical_path": [
                "TASK-001",
                "TASK-004",
                "TASK-006"
            ]
        }
