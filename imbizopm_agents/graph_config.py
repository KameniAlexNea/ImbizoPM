from langgraph.graph import END

from .agent_types import (
    ClarifierAgent,
    NegotiatorAgent,
    OutcomeAgent,
    PlannerAgent,
    PMAdapterAgent,
    RiskAgent,
    ScoperAgent,
    TaskifierAgent,
    TimelineAgent,
    ValidatorAgent,
)

# Default graph configuration
DEFAULT_GRAPH_CONFIG = {
    "nodes": {
        "ClarifierAgent": {
            "agent_class": ClarifierAgent,
            "description": "Refines the idea, extracts goals and constraints",
        },
        "OutcomeAgent": {
            "agent_class": OutcomeAgent,
            "description": "Defines success metrics and deliverables",
        },
        "PlannerAgent": {
            "agent_class": PlannerAgent,
            "description": "Breaks the project into phases, epics, and strategies",
        },
        "ScoperAgent": {
            "agent_class": ScoperAgent,
            "description": "Trims the plan into an MVP and resolves overload",
        },
        "TaskifierAgent": {
            "agent_class": TaskifierAgent,
            "description": "Produces detailed tasks with owners and dependencies",
        },
        "RiskAgent": {
            "agent_class": RiskAgent,
            "description": "Reviews feasibility and spots contradictions",
        },
        "TimelineAgent": {
            "agent_class": TimelineAgent,
            "description": "Maps tasks to durations and milestones",
        },
        "NegotiatorAgent": {
            "agent_class": NegotiatorAgent,
            "description": "Coordinates conflict resolution among agents",
        },
        "ValidatorAgent": {
            "agent_class": ValidatorAgent,
            "description": "Verifies alignment between idea, plan, and goals",
        },
        "PMAdapterAgent": {
            "agent_class": PMAdapterAgent,
            "description": "Formats and exports the project plan for external tools",
        },
    },
    "edges": {
        "ClarifierAgent": {"OutcomeAgent": "OutcomeAgent", END: END},
        "OutcomeAgent": {
            "ClarifierAgent": "ClarifierAgent",  # No Clear Outcome path
            "PlannerAgent": "PlannerAgent",
            END: END,
        },
        "PlannerAgent": {
            "ClarifierAgent": "ClarifierAgent",  # Too Vague path
            "ScoperAgent": "ScoperAgent",
            END: END,
        },
        "ScoperAgent": {
            "NegotiatorAgent": "NegotiatorAgent",  # Overload path
            "TaskifierAgent": "TaskifierAgent",
            END: END,
        },
        "TaskifierAgent": {
            "ClarifierAgent": "ClarifierAgent",  # Missing Info path
            "TimelineAgent": "TimelineAgent",
            END: END,
        },
        "TimelineAgent": {"RiskAgent": "RiskAgent", END: END},
        "RiskAgent": {
            "ValidatorAgent": "ValidatorAgent",
            "PlannerAgent": "PlannerAgent",  # Unfeasible path
            END: END,
        },
        "NegotiatorAgent": {
            "PlannerAgent": "PlannerAgent",
            "ScoperAgent": "ScoperAgent",
            END: END,
        },
        "ValidatorAgent": {
            "PMAdapterAgent": "PMAdapterAgent",  # Valid path
            "PlannerAgent": "PlannerAgent",  # Mismatch path
            END: END,
        },
        "PMAdapterAgent": {END: END},
    },
    "entry_point": "ClarifierAgent",
}
