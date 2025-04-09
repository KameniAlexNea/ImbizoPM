from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute
from .utils import format_list

PLANNER_PROMPT = """You are the Planner Agent. Your job is to create a structured project plan broken into logical phases, epics, and high-level strategies.

PROCESS:
1. Review the refined idea, goals, and deliverables
2. Determine the natural sequence of work required to achieve the outcomes
3. Group related activities into cohesive phases with clear objectives
4. Define major work areas (epics) that span across phases
5. Develop strategic approaches that will guide execution
6. Assess if sufficient information exists to create a meaningful plan

GUIDELINES:
- Each phase should have a clear start/end criteria and specific objectives
- Epics should encompass related tasks that deliver substantial value
- Strategies should address how to handle technical, resource, or risk challenges
- If the project lacks clarity, identify specific areas needing more information
- Ensure dependencies between phases and epics are logical

OUTPUT FORMAT:
{{
    "phases": [
        {{
            "name": "Descriptive phase name",
            "description": "Detailed phase description with clear objectives"
        }},
        ...
    ],
    "epics": [
        {{
            "name": "Descriptive epic name",
            "description": "Detailed epic description focusing on value delivered"
        }},
        ...
    ],
    "strategies": [
        {{
            "name": "Strategy name",
            "description": "Detailed description of the strategic approach"
        }},
        ...
    ],
    "too_vague": false,
    "vague_details": {{}}
}}

If the project is too vague to create a meaningful plan:
{{
    "too_vague": true,
    "vague_details": {{
        "unclear_aspects": [
            "Specific aspect of the project that lacks clarity",
            "..."
        ],
        "questions": [
            "Specific question that needs answering before planning can proceed",
            "..."
        ],
        "suggestions": [
            "Concrete suggestion to address the lack of clarity",
            "..."
        ]
    }},
    "phases": [],
    "epics": [],
    "strategies": []
}}"""


class PlannerAgent(BaseAgent):
    """Agent that breaks the project into phases, epics, and strategies."""

    def __init__(self, llm):
        super().__init__(llm, "Planner", PLANNER_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        prompt_parts = [f"Refined idea: {state['idea'].get('refined', '')}"]

        if state.get("goals"):
            prompt_parts.append(f"Goals:\n{format_list(state.get('goals', []))}")

        if state.get("constraints"):
            prompt_parts.append(
                f"Constraints:\n{format_list(state.get('constraints', []))}"
            )

        if state.get("outcomes"):
            prompt_parts.append(f"Outcomes:\n{format_list(state.get('outcomes', []))}")

        deliverables = [d.get("name", "") for d in state.get("deliverables", [])]
        if deliverables:
            prompt_parts.append(f"Deliverables:\n{format_list(deliverables)}")

        # Check for negotiation details from NegotiatorAgent
        if state.get("scope") and state["scope"].get("negotiation_details"):
            prompt_parts.append(
                f"Negotiation details:\n{state['scope'].get('negotiation_details')}"
            )

        prompt_parts.append("Break into phases, epics, and strategies.")

        return "\n".join(prompt_parts)

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["plan"] = {
            "phases": result.get("phases", []),
            "epics": result.get("epics", []),
            "strategies": result.get("strategies", []),
        }

        # Store feedback in plan dictionary if too vague
        if result.get("too_vague", False):
            state["plan"]["vague_feedback"] = result.get("vague_details", {})

        state["next"] = (
            AgentRoute.ClarifierAgent
            if result.get("too_vague", False)
            else AgentRoute.ScoperAgent
        )
        return state
