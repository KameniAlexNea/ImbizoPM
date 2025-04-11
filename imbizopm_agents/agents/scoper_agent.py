import json
from typing import Any, Dict, List, Literal, Union

from pydantic import BaseModel, Field

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute
from .utils import format_list


class MVPScope(BaseModel):
    features: List[str] = Field(
        default_factory=list,
        description="List of essential features that must be included in the MVP",
    )
    user_stories: List[str] = Field(
        default_factory=list,
        description="List of user stories in the format: 'As a [user type], I want [capability] so that [benefit]'",
    )


class Phase(BaseModel):
    phase: str = Field(description="Name of the phase (e.g., MVP, Phase 2)")
    description: str = Field(
        description="Detailed description of this phase’s focus and activities"
    )


class OverloadDetails(BaseModel):
    problem_areas: List[str] = Field(
        default_factory=list,
        description="Specific areas where the scope is too ambitious or exceeds resource constraints",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommended actions or trade-offs to reduce scope to a feasible level",
    )


class ScopeDefinitionBase(BaseModel):
    mvp_scope: MVPScope = Field(description="Core MVP features and user stories")
    scope_exclusions: List[str] = Field(
        default_factory=list,
        description="Capabilities explicitly excluded from MVP to maintain focus",
    )
    phased_approach: List[Phase] = Field(
        default_factory=list,
        description="Phases for delivering additional capabilities beyond MVP",
    )
    overload_details: OverloadDetails = Field(
        default_factory=OverloadDetails,
        description="Detailed explanation of any scope overload issues and suggestions",
    )


class NoScopeOverload(ScopeDefinitionBase):
    overload: Literal[False] = Field(
        default=False,
        description="Indicates that the current MVP scope is feasible without overload",
    )


class ScopeOverload(ScopeDefinitionBase):
    overload: Literal[True] = Field(
        default=True,
        description="Indicates that the scope is overloaded and needs to be reduced",
    )


ScopeDefinition = Union[NoScopeOverload, ScopeOverload]


SCOPER_OUTPUT = """OUTPUT FORMAT:
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
}}"""

SCOPER_PROMPT = f"""You are the Scoper Agent. Your job is to define a realistic Minimum Viable Product (MVP) and create a phased delivery approach that manages scope effectively.

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

{SCOPER_OUTPUT}"""


class ScoperAgent(BaseAgent):
    """Agent that trims the plan into an MVP and resolves overload."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.ScoperAgent,
            SCOPER_PROMPT,
            SCOPER_OUTPUT,
            ScopeDefinition if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        prompt_parts = [f"Refined idea:\n {state['idea'].get('refined', '')}"]

        if state["plan"].get("phases"):
            prompt_parts.append(
                f"Phases: {json.dumps(state['plan'].get('phases', []), indent=2)}"
            )

        if state["plan"].get("epics"):
            prompt_parts.append(
                f"Epics: {json.dumps(state['plan'].get('epics', []), indent=2)}"
            )

        if state.get("constraints"):
            prompt_parts.append(
                f"Constraints:\n{format_list(state.get('constraints', []))}"
            )

        # Check for negotiation details from NegotiatorAgent
        if state.get("warn_errors") and state["warn_errors"].get("negotiation_details"):
            prompt_parts.append(
                f"Negotiation details:\n{state['warn_errors'].get('negotiation_details')}"
            )
            state["warn_errors"].pop("negotiation_details")

        prompt_parts.append("Define MVP scope and resolve overload.")

        return "\n".join(prompt_parts)

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["scope"] = {
            "mvp": result.get("mvp_scope", {}),
            "exclusions": result.get("scope_exclusions", []),
            "phased_approach": result.get("phased_approach", []),
        }
        if result.get("overload", False):
            state["scope"]["overload"] = result.get("overload_details", {})
        state["next"] = (
            AgentRoute.NegotiatorAgent
            if result.get("overload", False) and result.get("overload_details", {})
            else AgentRoute.TaskifierAgent
        )
        state["current"] = AgentRoute.ScoperAgent
        return state
