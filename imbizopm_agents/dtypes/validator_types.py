from typing import Dict, List, Literal

from pydantic import BaseModel, Field


class GoalAlignment(BaseModel):
    aligned: Literal["Yes", "Partial", "No"] = Field(
        description="Whether the goal is fully, partially, or not aligned at all"
    )
    evidence: str = Field(
        description="Concrete elements of the plan showing alignment with the goal"
    )
    gaps: str = Field(
        description="Aspects of the goal not addressed in the current plan"
    )


class ConstraintRespect(BaseModel):
    respected: Literal["Yes", "Partial", "No"] = Field(
        description="Level to which the constraint is respected"
    )
    evidence: str = Field(
        description="Proof or reasoning showing respect for the constraint"
    )
    concerns: str = Field(
        description="Concerns or potential issues in respecting this constraint"
    )


class OutcomeAchievability(BaseModel):
    achievable: Literal["Yes", "Partial", "No"] = Field(
        description="Whether the outcome can reasonably be achieved"
    )
    evidence: str = Field(
        description="Justification for achievability based on the plan"
    )
    risks: str = Field(
        description="Risks or blockers that could hinder achieving the outcome"
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
        description="True if the plan is validated overall, else False"
    )
    alignment_score: str = Field(
        description='Score between "0%" and "100%" indicating alignment strength'
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

    @staticmethod
    def example() -> dict:
        """Return an example JSON representation of the PlanValidation model."""
        return {
            "overall_validation": True,
            "alignment_score": "85%",
            "goals_alignment": {
                "Increase user engagement by 30%": {
                    "aligned": "Yes",
                    "evidence": "The plan includes multiple features specifically designed to boost engagement, such as a gamification system, personalized notifications, and social sharing capabilities",
                    "gaps": "No specific metrics tracking mechanism is defined to measure the 30% improvement target",
                },
                "Reduce customer support inquiries by 50%": {
                    "aligned": "Partial",
                    "evidence": "The knowledge base and self-service troubleshooting tools will help users solve issues independently",
                    "gaps": "The plan lacks comprehensive user education components and proactive issue detection that would further reduce support needs",
                },
                "Launch in international markets within 6 months": {
                    "aligned": "No",
                    "evidence": "The current timeline shows domestic launch at month 5 with no explicit internationalization work",
                    "gaps": "The plan needs localization tasks, international payment processing, and regional compliance considerations",
                },
            },
            "constraints_respected": {
                "Maximum budget of $500,000": {
                    "respected": "Yes",
                    "evidence": "The resource allocation and cost projections total $475,000 including a 10% contingency buffer",
                    "concerns": "Integration costs with third-party services may fluctuate based on usage",
                },
                "Must comply with GDPR and CCPA regulations": {
                    "respected": "Partial",
                    "evidence": "Basic compliance features are included such as consent management and data export",
                    "concerns": "The plan doesn't address data retention policies or the right to be forgotten implementation details",
                },
                "Must integrate with existing ERP system": {
                    "respected": "Yes",
                    "evidence": "API integration tasks are explicitly included with appropriate time allocation",
                    "concerns": "The plan assumes current ERP API documentation is accurate and complete",
                },
            },
            "outcomes_achievable": {
                "Fully functional user dashboard": {
                    "achievable": "Yes",
                    "evidence": "The dashboard components are well-defined with dedicated development resources assigned",
                    "risks": "Timeline may be affected if design approval process takes longer than anticipated",
                },
                "Mobile application on iOS and Android": {
                    "achievable": "Partial",
                    "evidence": "Development resources are allocated for both platforms but may be stretched thin",
                    "risks": "Cross-platform compatibility issues may require additional testing time not fully accounted for",
                },
                "Integration with social media platforms": {
                    "achievable": "No",
                    "evidence": "The current resource allocation doesn't include specialized social media integration expertise",
                    "risks": "API changes from social platforms could introduce unexpected complexity and delays",
                },
            },
            "completeness_assessment": {
                "missing_elements": [
                    "Detailed risk mitigation strategies for major risks",
                    "Accessibility compliance verification process",
                    "Post-launch support and maintenance plan",
                    "User feedback collection and incorporation mechanism",
                ],
                "improvement_suggestions": [
                    "Add a dedicated risk assessment phase with explicit mitigation actions",
                    "Include an accessibility specialist in the QA team",
                    "Define KPIs for measuring success beyond the initial launch",
                    "Consider a phased rollout strategy to gather early feedback from beta users",
                ],
            },
        }
