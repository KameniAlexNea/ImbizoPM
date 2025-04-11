from typing import Literal

from pydantic import BaseModel, Field


class Risk(BaseModel):
    description: str = Field(description="Detailed description of the risk")
    category: Literal[
        "Technical", "Resource", "Timeline", "External", "Stakeholder"
    ] = Field(description="Category of the risk")
    impact: Literal["High", "Medium", "Low"] = Field(
        description="Impact level if the risk materializes"
    )
    probability: Literal["High", "Medium", "Low"] = Field(
        description="Likelihood of the risk occurring"
    )
    priority: Literal["High", "Medium", "Low"] = Field(
        description="Risk priority based on impact and probability"
    )
    mitigation_strategy: str = Field(
        description="Specific actions to reduce or prevent the risk"
    )
    contingency_plan: str = Field(description="Backup plan if the risk actually occurs")
