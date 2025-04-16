from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class GoalAlignment(BaseModel):
    aligned: str = Field(
        default="No",  # Added default
        description="Whether the goal is fully, partially, or not aligned at all. (Yes, Partial, No)",
    )
    evidence: str = Field(
        default="",  # Added default
        description="Concrete elements of the plan showing alignment with the goal",
    )
    gaps: Optional[list[str]] = Field(
        default_factory=list,
        description="Aspects of the goal not addressed in the current plan",
    )


class ConstraintRespect(BaseModel):
    respected: str = Field(
        default="No",  # Added default
        description="Level to which the constraint is respected. (Yes, Partial, No)",
    )
    evidence: str = Field(
        default="",  # Added default
        description="Proof or reasoning showing respect for the constraint",
    )
    concerns: Optional[list[str]] = Field(
        default_factory=list,
        description="Concerns or potential issues in respecting this constraint",
    )


class OutcomeAchievability(BaseModel):
    achievable: str = Field(
        default="No",  # Added default
        description="Whether the outcome can reasonably be achieved. (Yes, Partial, No)",
    )
    evidence: str = Field(
        default="",  # Added default
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
    goals_alignment: Dict[str, GoalAlignment] = Field(
        default_factory=dict,
        description="Mapping from goal names to their alignment evaluation",
    )
    constraints_respected: Dict[str, ConstraintRespect] = Field(
        default_factory=dict,
        description="Mapping from constraint names to their respect status",
    )
    outcomes_achievable: Dict[str, OutcomeAchievability] = Field(
        default_factory=dict,
        description="Mapping from outcome names to achievability assessment",
    )
    completeness_assessment: CompletenessAssessment = Field(
        default_factory=CompletenessAssessment,
        description="Summary of what's missing and how the plan could be improved",
    )

    def to_structured_string(self) -> str:
        """Formats the plan validation results into a structured string."""
        validation_status = "Validated" if self.overall_validation else "Not Validated"
        output = f"**Plan Validation Status: {validation_status}**\n"
        output += f"**Overall Alignment Score:** {self.alignment_score}\n\n"

        if not self.overall_validation:
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
            # Optionally add details from other sections even if not validated overall
            # For brevity, we focus on completeness when not validated.

        else:
            if self.goals_alignment:
                output += "**Goals Alignment:**\n"
                for goal, alignment in self.goals_alignment.items():
                    output += f"- **Goal:** {goal}\n"
                    output += f"  - **Alignment:** {alignment.aligned}\n"
                    output += f"  - **Evidence:** {alignment.evidence}\n"
                    if alignment.gaps:
                        output += f"  - **Gaps:** {'; '.join(alignment.gaps)}\n"
                output += "\n"

            if self.constraints_respected:
                output += "**Constraints Respected:**\n"
                for constraint, respect in self.constraints_respected.items():
                    output += f"- **Constraint:** {constraint}\n"
                    output += f"  - **Respected:** {respect.respected}\n"
                    output += f"  - **Evidence:** {respect.evidence}\n"
                    if respect.concerns:
                        output += f"  - **Concerns:** {'; '.join(respect.concerns)}\n"
                output += "\n"

            if self.outcomes_achievable:
                output += "**Outcomes Achievability:**\n"
                for outcome, achievability in self.outcomes_achievable.items():
                    output += f"- **Outcome:** {outcome}\n"
                    output += f"  - **Achievable:** {achievability.achievable}\n"
                    output += f"  - **Evidence:** {achievability.evidence}\n"
                    if achievability.risks:
                        output += f"  - **Risks:** {'; '.join(achievability.risks)}\n"
                output += "\n"

            # Include completeness even if validated, if there are items
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
                "goals_alignment": {
                    "Launch a basic informational website": {
                        "aligned": "Yes",
                        "evidence": "Plan includes tasks for design, content, development, and deployment of core pages (menu, contact).",
                        "gaps": [],
                    },
                    "Ensure the website is mobile-friendly": {
                        "aligned": "Yes",
                        "evidence": "Task T4 specifically addresses mobile responsiveness.",
                        "gaps": [],
                    },
                },
                "constraints_respected": {
                    "Budget: $1000": {
                        "respected": "Yes",
                        "evidence": "Estimated effort for tasks aligns with typical costs for a simple site within this budget.",
                        "concerns": ["Assumes no major scope changes."],
                    },
                    "Timeline: 4 weeks": {
                        "respected": "Yes",
                        "evidence": "Timeline estimates T+20 days for launch, fitting within 4 weeks.",
                        "concerns": ["Dependent on timely content delivery (Task T2)."],
                    },
                },
                "outcomes_achievable": {
                    "Live website with menu and contact info": {
                        "achievable": "Yes",
                        "evidence": "Tasks cover all necessary steps from design to deployment.",
                        "risks": ["Potential delays if content (T2) is late."],
                    },
                },
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
                "goals_alignment": {
                    "Launch a basic informational website": {
                        "aligned": "Partial",
                        "evidence": "Tasks exist, but key dependencies are missing.",
                        "gaps": ["No task for acquiring hosting or domain."],
                    }
                },
                "constraints_respected": {
                    "Budget: $1000": {
                        "respected": "No",
                        "evidence": "Plan lacks cost estimation for hosting/domain.",
                        "concerns": ["Budget likely insufficient if hosting costs are high."],
                    }
                },
                "outcomes_achievable": {
                    "Live website with menu and contact info": {
                        "achievable": "No",
                        "evidence": "Cannot launch without hosting/domain.",
                        "risks": ["Project blocked until hosting/domain are secured."],
                    }
                },
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
