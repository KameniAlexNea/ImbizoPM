from typing import List

from pydantic import BaseModel, Field


class ProjectPlan(BaseModel):
    refined_idea: str = Field(
        description="A clear, concise statement of what the project aims to accomplish"
    )
    goals: List[str] = Field(
        default_factory=list,
        description="A list of specific, measurable goals that address core needs with clear success criteria",
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="A list of specific limitations or boundaries that must be respected during the project",
    )
