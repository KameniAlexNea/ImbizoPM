from typing import List, Optional

from pydantic import BaseModel, Field


class GoalAlignment(BaseModel):
    name: str = Field(
        description="The name or description of the goal"
    )  # Added name field
    aligned: str = Field(
        default="No",
        description="Whether the goal is fully, partially, or not aligned at all. (Yes, Partial, No)",
    )
    evidence: str = Field(
        default="",
        description="Concrete elements of the plan showing alignment with the goal",
    )
    gaps: Optional[list[str]] = Field(
        default_factory=list,
        description="Aspects of the goal not addressed in the current plan",
    )


class ConstraintRespect(BaseModel):
    name: str = Field(
        description="The name or description of the constraint"
    )  # Added name field
    respected: str = Field(
        default="No",
        description="Level to which the constraint is respected. (Yes, Partial, No)",
    )
    evidence: str = Field(
        default="",
        description="Proof or reasoning showing respect for the constraint",
    )
    concerns: Optional[list[str]] = Field(
        default_factory=list,
        description="Concerns or potential issues in respecting this constraint",
    )


class OutcomeAchievability(BaseModel):
    name: str = Field(
        description="The name or description of the outcome"
    )  # Added name field
    achievable: str = Field(
        default="No",
        description="Whether the outcome can reasonably be achieved. (Yes, Partial, No)",
    )
    evidence: str = Field(
        default="",
        description="Justification for achievability based on the plan",
    )
    risks: Optional[list[str]] = Field(
        default_factory=list,
        description="Risks or blockers that could hinder achieving the outcome",
    )


class CompletenessAssessment(BaseModel):
    missing_elements: List[str] = Field(
        default_factory=list,
        description="List of important elements missing from the plan",
    )
    improvement_suggestions: List[str] = Field(
        default_factory=list,
        description="Ideas or tips to improve the plan's completeness",
    )


class PlanValidation(BaseModel):
    overall_validation: bool = Field(
        default=False, description="True if the plan is validated overall, else False"
    )
    alignment_score: str = Field(
        default="",
        description='Score between "0%" and "100%" indicating alignment strength',
    )
    goals_alignment: List[GoalAlignment] = Field(  # Changed from Dict to List
        default_factory=list,
        description="List of goal alignment evaluations",
    )
    constraints_respected: List[ConstraintRespect] = Field(  # Changed from Dict to List
        default_factory=list,
        description="List of constraint respect statuses",
    )
    outcomes_achievable: List[OutcomeAchievability] = (
        Field(  # Changed from Dict to List
            default_factory=list,
            description="List of outcome achievability assessments",
        )
    )
    completeness_assessment: CompletenessAssessment = Field(
        default_factory=CompletenessAssessment,
        description="Summary of what's missing and how the plan could be improved",
    )

    def is_valid(self):
        return (
            self.overall_validation
            or self.completeness_assessment is None
            or not self.completeness_assessment.missing_elements
        )

    def to_structured_string(self) -> str:
        """Formats the plan validation results into a structured string."""
        validation_status = "Validated" if self.is_valid() else "Not Validated"
        output = f"**Plan Validation Status: {validation_status}**\n"
        output += f"**Overall Alignment Score:** {self.alignment_score}\n\n"

        if not self.is_valid():
            output += "**Completeness Assessment (Issues Found):**\n"
            if self.completeness_assessment.missing_elements:
                output += "*   **Missing Elements:**\n"
                for element in self.completeness_assessment.missing_elements:
                    output += f"    - {element}\n"
            if self.completeness_assessment.improvement_suggestions:
                output += "*   **Improvement Suggestions:**\n"
                for suggestion in self.completeness_assessment.improvement_suggestions:
                    output += f"    - {suggestion}\n"
            output += "\n"

        else:
            if self.goals_alignment:
                output += "**Goals Alignment:**\n"
                for alignment in self.goals_alignment:  # Iterate over list
                    output += f"- **Goal:** {alignment.name}\n"  # Access name field
                    output += f"  - **Alignment:** {alignment.aligned}\n"
                    output += f"  - **Evidence:** {alignment.evidence}\n"
                    if alignment.gaps:
                        output += f"  - **Gaps:** {'; '.join(alignment.gaps)}\n"
                output += "\n"

            if self.constraints_respected:
                output += "**Constraints Respected:**\n"
                for respect in self.constraints_respected:  # Iterate over list
                    output += f"- **Constraint:** {respect.name}\n"  # Access name field
                    output += f"  - **Respected:** {respect.respected}\n"
                    output += f"  - **Evidence:** {respect.evidence}\n"
                    if respect.concerns:
                        output += f"  - **Concerns:** {'; '.join(respect.concerns)}\n"
                output += "\n"

            if self.outcomes_achievable:
                output += "**Outcomes Achievability:**\n"
                for achievability in self.outcomes_achievable:  # Iterate over list
                    output += (
                        f"- **Outcome:** {achievability.name}\n"  # Access name field
                    )
                    output += f"  - **Achievable:** {achievability.achievable}\n"
                    output += f"  - **Evidence:** {achievability.evidence}\n"
                    if achievability.risks:
                        output += f"  - **Risks:** {'; '.join(achievability.risks)}\n"
                output += "\n"

            if (
                self.completeness_assessment.missing_elements
                or self.completeness_assessment.improvement_suggestions
            ):
                output += "**Completeness Assessment:**\n"
                if self.completeness_assessment.missing_elements:
                    output += "*   **Missing Elements:**\n"
                    for element in self.completeness_assessment.missing_elements:
                        output += f"    - {element}\n"
                if self.completeness_assessment.improvement_suggestions:
                    output += "*   **Improvement Suggestions:**\n"
                    for (
                        suggestion
                    ) in self.completeness_assessment.improvement_suggestions:
                        output += f"    - {suggestion}\n"
                output += "\n"

        return output.strip()

    @staticmethod
    def example() -> dict:
        """Return simpler examples of both validated and not validated PlanValidation models."""
        return {
            "validated": {
                "overall_validation": True,
                "alignment_score": "90%",
                "goals_alignment": [  # Changed to list
                    {
                        "name": "Launch a basic informational website",  # Added name
                        "aligned": "Yes",
                        "evidence": "Plan includes tasks for design, content, development, and deployment of core pages (menu, contact).",
                        "gaps": [],
                    },
                    {
                        "name": "Ensure the website is mobile-friendly",  # Added name
                        "aligned": "Yes",
                        "evidence": "Task T4 specifically addresses mobile responsiveness.",
                        "gaps": [],
                    },
                ],
                "constraints_respected": [  # Changed to list
                    {
                        "name": "Budget: $1000",  # Added name
                        "respected": "Yes",
                        "evidence": "Estimated effort for tasks aligns with typical costs for a simple site within this budget.",
                        "concerns": ["Assumes no major scope changes."],
                    },
                    {
                        "name": "Timeline: 4 weeks",  # Added name
                        "respected": "Yes",
                        "evidence": "Timeline estimates T+20 days for launch, fitting within 4 weeks.",
                        "concerns": ["Dependent on timely content delivery (Task T2)."],
                    },
                ],
                "outcomes_achievable": [  # Changed to list
                    {
                        "name": "Live website with menu and contact info",  # Added name
                        "achievable": "Yes",
                        "evidence": "Tasks cover all necessary steps from design to deployment.",
                        "risks": ["Potential delays if content (T2) is late."],
                    },
                ],
                "completeness_assessment": {
                    "missing_elements": [],
                    "improvement_suggestions": [
                        "Consider adding a task for basic SEO setup.",
                        "Explicitly mention browser compatibility testing.",
                    ],
                },
            },
            "not_validated": {
                "overall_validation": False,
                "alignment_score": "40%",
                "goals_alignment": [  # Changed to list
                    {
                        "name": "Launch a basic informational website",  # Added name
                        "aligned": "Partial",
                        "evidence": "Tasks exist, but key dependencies are missing.",
                        "gaps": ["No task for acquiring hosting or domain."],
                    }
                ],
                "constraints_respected": [  # Changed to list
                    {
                        "name": "Budget: $1000",  # Added name
                        "respected": "No",
                        "evidence": "Plan lacks cost estimation for hosting/domain.",
                        "concerns": [
                            "Budget likely insufficient if hosting costs are high."
                        ],
                    }
                ],
                "outcomes_achievable": [  # Changed to list
                    {
                        "name": "Live website with menu and contact info",  # Added name
                        "achievable": "No",
                        "evidence": "Cannot launch without hosting/domain.",
                        "risks": ["Project blocked until hosting/domain are secured."],
                    }
                ],
                "completeness_assessment": {
                    "missing_elements": [
                        "Task for selecting and purchasing hosting.",
                        "Task for registering or configuring domain name.",
                        "Clear definition of who provides final content approval.",
                        "Plan for website maintenance post-launch.",
                    ],
                    "improvement_suggestions": [
                        "Add tasks for infrastructure setup (hosting, domain).",
                        "Clarify content approval process.",
                        "Discuss post-launch support needs.",
                    ],
                },
            },
        }
