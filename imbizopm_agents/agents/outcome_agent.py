from typing import Any, Dict, List

from ..base_agent import AgentState, BaseAgent
from ..dtypes.outcome_types import Deliverable, ProjectSuccessCriteria
from .agent_routes import AgentRoute
from .utils import format_list


OUTCOME_OUTPUT = """OUTPUT FORMAT:
{{
    "success_metrics": [
        "Specific measurement that indicates goal achievement (target value, measurement method)",
        "Another concrete metric with clear threshold for success",
        "..."
    ],
    "deliverables": [
        {{
            "name": "Clear name of deliverable",
            "description": "Detailed description of what this deliverable includes"
        }},
        ...
    ]
}}"""

OUTCOME_PROMPT = f"""You are the Outcome Agent. Your job is to define concrete success metrics and deliverables that will satisfy the refined idea and goals.

PROCESS:
1. Analyze the refined idea and goals
2. For each goal, determine how success will be measured objectively
3. Identify all tangible outputs that must be produced
4. Ensure each deliverable directly contributes to at least one goal
5. Verify that the metrics are realistic and measurable

GUIDELINES:
- Each success metric should be specific, measurable, and time-bound
- Deliverables should be concrete artifacts that stakeholders can review
- Consider both quantitative metrics (numbers) and qualitative metrics (satisfaction)
- Ensure the combined deliverables will fully satisfy the project goals
- Avoid vanity metrics that don't directly indicate success

{OUTCOME_OUTPUT}"""


class OutcomeAgent(BaseAgent):
    """Agent that defines success metrics and deliverables."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.OutcomeAgent,
            OUTCOME_PROMPT,
            OUTCOME_OUTPUT,
            ProjectSuccessCriteria if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""Refined idea:
{state['idea'].get('refined', '')}
Goals:
{format_list(state.get('goals', []))}
Constraints:
{format_list(state.get('constraints', []))}

Define success metrics and deliverables."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        # Extract data with more robust error handling
        success_metrics = result.get("success_metrics", [])
        deliverables = result.get("deliverables", [])

        # Add the data to state
        state["outcomes"] = success_metrics
        state["deliverables"] = deliverables

        # Determine next step based on presence of outcomes
        state["next"] = (
            AgentRoute.PlannerAgent if success_metrics else AgentRoute.ClarifierAgent
        )
        state["current"] = AgentRoute.OutcomeAgent

        return state
