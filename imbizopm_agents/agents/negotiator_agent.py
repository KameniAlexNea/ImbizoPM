from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute

NEGOCIATOR_PROMPT = """You are the Negotiator Agent. Your job is to identify and resolve conflicts between different aspects of the project plan and propose balanced solutions.

PROCESS:
1. Review all components of the project plan
2. Identify inconsistencies, contradictions, or competing priorities
3. Analyze the source and impact of each conflict
4. Propose specific solutions that balance competing needs
5. Prioritize changes based on impact to project success
6. Consider tradeoffs between scope, time, quality, and resources

GUIDELINES:
- Look for conflicts between goals, constraints, timeline, and resources
- Identify where agents have made contradictory assumptions
- Consider stakeholder perspectives when proposing solutions
- Focus on preserving core value while making necessary compromises
- Be specific about what needs to change and why
- Document tradeoffs explicitly so stakeholders understand implications

OUTPUT FORMAT:
{{
	"conflict_area": "scope", // or "plan"
	"negotiation_details": {{
		"issues": ["<specific issue>", "..."],
		"proposed_solutions": ["<solution>", "..."],
		"priorities": ["<priority>", "..."]
	}}
}}"""


class NegotiatorAgent(BaseAgent):
    """Agent that coordinates conflict resolution among agents."""

    def __init__(self, llm):
        super().__init__(llm, AgentRoute.NegotiatorAgent, NEGOCIATOR_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        # Identify which aspect has conflicts
        return f"""Refined idea: {state['idea'].get('refined', '')}
Plan: {state['plan']}
Scope: {state['scope']}

Consider the plan and scope. Identify any conflicts or inconsistencies between them."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        # Store negotiation details in scope dictionary
        if result.get("negotiation_details"):
            if "scope" not in state:
                state["scope"] = {}
            state["warn_errors"]["negotiation_details"] = result.get("negotiation_details")

        # Based on which aspect was negotiated, return to the appropriate agent
        conflict_area = result.get("conflict_area", "")
        state["next"] = (
            AgentRoute.ScoperAgent
            if conflict_area == "scope"
            else AgentRoute.PlannerAgent
        )
        state["current"] = AgentRoute.NegotiatorAgent
        return state
