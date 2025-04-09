from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute
from .utils import format_list

OUTCOME_PROMPT = """You are the Outcome Agent. Your job is to define concrete success metrics and deliverables that will satisfy the refined idea and goals.

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

OUTPUT FORMAT:
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

class OutcomeAgent(BaseAgent):
    """Agent that defines success metrics and deliverables."""

    def __init__(self, llm):
        super().__init__(llm, "Outcome", OUTCOME_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""Refined idea:
{state['idea'].get('refined', '')}
Goals:
{format_list(state.get('goals', []))}
Constraints:
{format_list(state.get('constraints', []))}

Define success metrics and deliverables."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["outcomes"] = result.get("success_metrics", [])
        state["deliverables"] = result.get("deliverables", [])
        state["next"] = AgentRoute.PlannerAgent if state["outcomes"] else AgentRoute.ClarifierAgent
        return state
