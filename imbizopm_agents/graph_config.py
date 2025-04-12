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

"""
flowchart TD
    A[User Idea] --> B[ClarifierAgent]
    B --> C[OutcomeAgent]
    C --> D[PlannerAgent]
    D --> E[ScoperAgent]
    E --> F[TaskifierAgent]
    F --> G[TimelineAgent]
    G --> H[RiskAgent]
    H --> I[ValidatorAgent]
    I -->|Valid| J[PMAdapterAgent]
    I -->|Mismatch| D
    H -->|Unfeasible| D
    E -->|Overload| Negotiator[NegotiatorAgent]
    D -->|Too Vague| B
    F -->|Missing Info| B
    C -->|No Clear Outcome| B
"""

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
        "ClarifierAgent": ["OutcomeAgent"],
        "OutcomeAgent": {
            "ClarifierAgent": "ClarifierAgent",  # No Clear Outcome path
            "PlannerAgent": "PlannerAgent",
        },
        "PlannerAgent": {
            "ClarifierAgent": "ClarifierAgent",  # Too Vague path
            "ScoperAgent": "ScoperAgent",
            "NegotiatorAgent": "NegotiatorAgent",  # If previous plan is negotiated
        },
        "ScoperAgent": {
            "NegotiatorAgent": "NegotiatorAgent",  # Overload path
            "TaskifierAgent": "TaskifierAgent",
        },
        "TaskifierAgent": {
            "ClarifierAgent": "ClarifierAgent",  # Missing Info path
            "TimelineAgent": "TimelineAgent",
        },
        "TimelineAgent": ["RiskAgent"],
        "RiskAgent": {
            "ValidatorAgent": "ValidatorAgent",
            "PlannerAgent": "PlannerAgent",  # Unfeasible path
        },
        "NegotiatorAgent": {
            "PlannerAgent": "PlannerAgent",
            "ScoperAgent": "ScoperAgent",
        },
        "ValidatorAgent": {
            "PMAdapterAgent": "PMAdapterAgent",  # Valid path
            "PlannerAgent": "PlannerAgent",  # Mismatch path
        },
        "PMAdapterAgent": [END],
    },
    "entry_point": "ClarifierAgent",
}

NodeSuffix = "Node"
