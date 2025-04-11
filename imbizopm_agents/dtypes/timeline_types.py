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
