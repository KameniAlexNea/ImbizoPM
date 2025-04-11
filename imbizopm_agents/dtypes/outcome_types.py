from typing import List

from pydantic import BaseModel, Field


class Deliverable(BaseModel):
    name: str = Field(description="Clear name of the deliverable")
    description: str = Field(
        description="Detailed description of what this deliverable includes"
    )


class ProjectSuccessCriteria(BaseModel):
    success_metrics: List[str] = Field(
        default_factory=list,
        description="List of specific measurements that indicate goal achievement (e.g., target value, method of measurement)",
    )
    deliverables: List[Deliverable] = Field(
        default_factory=list,
        description="List of key deliverables, each defined by a name and detailed description",
    )
