from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute
from .utils import format_list

SCOPER_PROMPT = """You are the Scoper Agent. Your job is to define a realistic Minimum Viable Product (MVP) and create a phased delivery approach that manages scope effectively.

PROCESS:
1. Review the full project plan, deliverables, and goals
2. Identify the minimum features needed to deliver core value
3. Explicitly exclude nice-to-have features from the MVP
4. Develop a phased approach to incrementally deliver value
5. Check for scope overload and make recommendations for scope reduction if needed

GUIDELINES:
- The MVP should focus only on features essential to test core hypotheses
- User stories should represent the perspective of actual end users
- Scope exclusions should be explicit to prevent scope creep
- The phased approach should prioritize features by value and dependencies
- Consider technical debt and foundation work in early phases

OUTPUT FORMAT:
{{
    "mvp_scope": {{
        "features": [
            "Essential feature that delivers core value",
            "..."
        ],
        "user_stories": [
            "As a [user type], I want [capability] so that [benefit]",
            "..."
        ]
    }},
    "scope_exclusions": [
        "Specific feature/capability explicitly excluded from MVP scope",
        "..."
    ],
    "phased_approach": [
        {{
            "phase": "Phase name (e.g., MVP, Phase 2, etc.)",
            "description": "Detailed description of this phase's focus"
        }},
        ...
    ]
    "overload": false,
    "overload_details": {{
        "problem_areas": [],
        "recommendations": []
    }}
}}

// Alternative output if scope overload is detected:
{{
    "overload": true,
    "overload_details": {{
        "problem_areas": [
            "Specific area where scope exceeds realistic constraints",
            "..."
        ],
        "recommendations": [
            "Specific recommendation to reduce scope",
            "..."
        ]
    }},
    "mvp_scope": {{
        "features": ["..."],
        "user_stories": ["..."]
    }},
    "scope_exclusions": ["..."],
    "phased_approach": ["..."]
}}
"""


class ScoperAgent(BaseAgent):
    """Agent that trims the plan into an MVP and resolves overload."""

    def __init__(self, llm):
        super().__init__(llm, "Scoper", SCOPER_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        prompt_parts = []

        if state["plan"].get("phases"):
            prompt_parts.append(f"Phases: {state['plan'].get('phases', [])}")

        if state["plan"].get("epics"):
            prompt_parts.append(f"Epics: {state['plan'].get('epics', [])}")

        if state.get("constraints"):
            prompt_parts.append(
                f"Constraints:\n{format_list(state.get('constraints', []))}"
            )

        # Check for negotiation details from NegotiatorAgent
        if state.get("scope") and state["scope"].get("negotiation_details"):
            prompt_parts.append(
                f"Negotiation details:\n{state['scope'].get('negotiation_details')}"
            )

        prompt_parts.append("Define MVP scope and resolve overload.")

        return "\n".join(prompt_parts)

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["scope"] = {
            "mvp": result.get("mvp_scope", {}),
            "exclusions": result.get("scope_exclusions", []),
            "phased_approach": result.get("phased_approach", []),
        }
        state["next"] = (
            AgentRoute.NegotiatorAgent
            if result.get("overload", False)
            else AgentRoute.TaskifierAgent
        )
        return state
