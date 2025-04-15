from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class GoalAlignment(BaseModel):
    aligned: Literal["Yes", "Partial", "No"] = Field(
        default="No",  # Added default
        description="Whether the goal is fully, partially, or not aligned at all",
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
    respected: Literal["Yes", "Partial", "No"] = Field(
        default="No",  # Added default
        description="Level to which the constraint is respected",
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
    achievable: Literal["Yes", "Partial", "No"] = Field(
        default="No",  # Added default
        description="Whether the outcome can reasonably be achieved",
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
        """Return an example JSON representation of the PlanValidation model."""
        return {
            "validated": {
                "overall_validation": True,
                "alignment_score": "85%",
                "goals_alignment": {
                    "Increase user engagement by 30%": {
                        "aligned": "Yes",
                        "evidence": "The plan includes multiple features specifically designed to boost engagement, such as a gamification system, personalized notifications, and social sharing capabilities",
                        "gaps": [
                            "No specific metrics tracking mechanism is defined to measure the 30% improvement target"
                        ],
                    },
                    "Reduce customer support inquiries by 50%": {
                        "aligned": "Partial",
                        "evidence": "The knowledge base and self-service troubleshooting tools will help users solve issues independently",
                        "gaps": [
                            "The plan lacks comprehensive user education components and proactive issue detection that would further reduce support needs"
                        ],
                    },
                    "Launch in international markets within 6 months": {
                        "aligned": "No",
                        "evidence": "The current timeline shows domestic launch at month 5 with no explicit internationalization work",
                        "gaps": [
                            "The plan needs localization tasks, international payment processing, and regional compliance considerations"
                        ],
                    },
                },
                "constraints_respected": {
                    "Maximum budget of $500,000": {
                        "respected": "Yes",
                        "evidence": "The resource allocation and cost projections total $475,000 including a 10% contingency buffer",
                        "concerns": [
                            "Integration costs with third-party services may fluctuate based on usage"
                        ],
                    },
                    "Must comply with GDPR and CCPA regulations": {
                        "respected": "Partial",
                        "evidence": "Basic compliance features are included such as consent management and data export",
                        "concerns": [
                            "The plan doesn't address data retention policies or the right to be forgotten implementation details"
                        ],
                    },
                    "Must integrate with existing ERP system": {
                        "respected": "Yes",
                        "evidence": "API integration tasks are explicitly included with appropriate time allocation",
                        "concerns": [
                            "The plan assumes current ERP API documentation is accurate and complete"
                        ],
                    },
                },
                "outcomes_achievable": {
                    "Fully functional user dashboard": {
                        "achievable": "Yes",
                        "evidence": "The dashboard components are well-defined with dedicated development resources assigned",
                        "risks": [
                            "Timeline may be affected if design approval process takes longer than anticipated"
                        ],
                    },
                    "Mobile application on iOS and Android": {
                        "achievable": "Partial",
                        "evidence": "Development resources are allocated for both platforms but may be stretched thin",
                        "risks": [
                            "Cross-platform compatibility issues may require additional testing time not fully accounted for"
                        ],
                    },
                    "Integration with social media platforms": {
                        "achievable": "No",
                        "evidence": "The current resource allocation doesn't include specialized social media integration expertise",
                        "risks": [
                            "API changes from social platforms could introduce unexpected complexity and delays"
                        ],
                    },
                },
                "completeness_assessment": {
                    "missing_elements": [],
                    "improvement_suggestions": [],
                },
            },
            "not_validated": {
                "overall_validation": False,
                "alignment_score": "35%",
                "goals_alignment": {},
                "constraints_respected": {},
                "outcomes_achievable": {},
                "completeness_assessment": {
                    "missing_elements": [
                        "Detailed risk mitigation strategies for major risks",
                        "Accessibility compliance verification process",
                        "Post-launch support and maintenance plan",
                        "User feedback collection and incorporation mechanism",
                        "Comprehensive testing strategy across environments",
                        "Detailed resource allocation and team structure",
                        "Change management and stakeholder communication plan",
                        "Performance metrics and monitoring framework",
                    ],
                    "improvement_suggestions": [
                        "Add a dedicated risk assessment phase with explicit mitigation actions",
                        "Include an accessibility specialist in the QA team",
                        "Define KPIs for measuring success beyond the initial launch",
                        "Consider a phased rollout strategy to gather early feedback from beta users",
                        "Develop a detailed testing plan including load testing and security audits",
                        "Create a more detailed project timeline with clear dependencies",
                        "Include budget contingencies for unforeseen technical challenges",
                        "Establish regular review checkpoints to assess project health",
                    ],
                },
            },
        }
