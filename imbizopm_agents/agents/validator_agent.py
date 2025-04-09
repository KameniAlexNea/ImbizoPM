from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute

VALIDATOR_PROMPT = """You are the Validator Agent. Your job is to verify that the final project plan aligns with the original goals, respects all constraints, and will deliver the expected outcomes.

PROCESS:
1. Compare the original idea and refined goals with the final plan
2. Check that all constraints are respected in the plan
3. Verify that the planned deliverables will achieve the desired outcomes
4. Assess the completeness and coherence of the overall plan
5. Identify any gaps or misalignments

GUIDELINES:
- Analyze each goal individually to verify the plan addresses it
- Check each constraint to ensure the plan respects its limitations
- Verify that success metrics are addressed by specific elements in the plan
- Look for logical inconsistencies or missing components
- Consider the project from stakeholder perspectives

OUTPUT FORMAT:
{{
    "overall_validation": "Pass/Fail",
    "alignment_score": "0-100%",
    "goals_alignment": {{
        "Goal 1": {{
            "aligned": "Yes/Partial/No",
            "evidence": "Specific elements in the plan that address this goal",
            "gaps": "Any aspects of the goal not adequately addressed"
        }},
        "..."
    }},
    "constraints_respected": {{
        "Constraint 1": {{
            "respected": "Yes/Partial/No",
            "evidence": "How the plan respects this constraint",
            "concerns": "Any potential violations or risks"
        }},
        "..."
    }},
    "outcomes_achievable": {{
        "Outcome 1": {{
            "achievable": "Yes/Partial/No",
            "evidence": "Elements in the plan that will deliver this outcome",
            "risks": "Factors that might prevent achievement"
        }},
        "..."
    }},
    "completeness_assessment": {{
        "missing_elements": [
            "Specific element missing from the plan",
            "..."
        ],
        "improvement_suggestions": [
            "Specific suggestion to improve plan completeness",
            "..."
        ]
    }}
}}"""


class ValidatorAgent(BaseAgent):
    """Agent that verifies alignment between idea, plan, and goals."""

    def __init__(self, llm):
        super().__init__(llm, "Validator", VALIDATOR_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""
Original idea: {state['idea'].get('refined', '')}
Goals: {', '.join(state['goals'])}
Constraints: {', '.join(state['constraints'])}
Outcomes: {', '.join(state['outcomes'])}
Plan: {state['plan']}
Scope: {state['scope']}
Tasks: {state['tasks']}

Validate alignment between the idea, goals, and the resulting plan."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["validation"] = {
            "goals_alignment": result.get("goals_alignment", {}),
            "constraints_respected": result.get("constraints_respected", {}),
            "outcomes_achievable": result.get("outcomes_achievable", {}),
            "overall": result.get("overall_validation", False),
        }

        # Check validation result
        state["next"] = AgentRoute.PMAdapterAgent if state["validation"]["overall"] else AgentRoute.PlannerAgent
        return state
