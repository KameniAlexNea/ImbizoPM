from typing import Dict, List, Optional, Type, Union

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.types import Command, interrupt

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
from .base_agent import AgentState, BaseAgent
# Default graph configuration
DEFAULT_GRAPH_CONFIG = {
    "nodes": {
        "ClarifierAgent": {
            "agent_class": ClarifierAgent,
            "description": "Refines the idea, extracts goals and constraints"
        },
        "OutcomeAgent": {
            "agent_class": OutcomeAgent,
            "description": "Defines success metrics and deliverables"
        },
        "PlannerAgent": {
            "agent_class": PlannerAgent,
            "description": "Breaks the project into phases, epics, and strategies"
        },
        "ScoperAgent": {
            "agent_class": ScoperAgent,
            "description": "Trims the plan into an MVP and resolves overload"
        },
        "TaskifierAgent": {
            "agent_class": TaskifierAgent,
            "description": "Produces detailed tasks with owners and dependencies"
        },
        "RiskAgent": {
            "agent_class": RiskAgent,
            "description": "Reviews feasibility and spots contradictions"
        },
        "TimelineAgent": {
            "agent_class": TimelineAgent,
            "description": "Maps tasks to durations and milestones"
        },
        "NegotiatorAgent": {
            "agent_class": NegotiatorAgent,
            "description": "Coordinates conflict resolution among agents"
        },
        "ValidatorAgent": {
            "agent_class": ValidatorAgent,
            "description": "Verifies alignment between idea, plan, and goals"
        },
        "PMAdapterAgent": {
            "agent_class": PMAdapterAgent,
            "description": "Formats and exports the project plan for external tools"
        },
        "HumanAssistance": {
            "is_tool": True,
            "description": "Requests assistance from a human"
        }
    },
    "edges": {
        "ClarifierAgent": {
            "OutcomeAgent": "OutcomeAgent",
            END: END
        },
        "OutcomeAgent": {
            "ClarifierAgent": "ClarifierAgent",
            "PlannerAgent": "PlannerAgent",
            END: END
        },
        "PlannerAgent": {
            "ScoperAgent": "ScoperAgent",
            END: END
        },
        "ScoperAgent": {
            "NegotiatorAgent": "NegotiatorAgent",
            "TaskifierAgent": "TaskifierAgent",
            END: END
        },
        "TaskifierAgent": {
            "ClarifierAgent": "ClarifierAgent",
            "TimelineAgent": "TimelineAgent",
            END: END
        },
        "TimelineAgent": {
            "RiskAgent": "RiskAgent",
            END: END
        },
        "RiskAgent": {
            "ValidatorAgent": "ValidatorAgent",
            "PlannerAgent": "PlannerAgent",
            END: END
        },
        "NegotiatorAgent": {
            "PlannerAgent": "PlannerAgent",
            "ScoperAgent": "ScoperAgent",
            END: END
        },
        "ValidatorAgent": {
            "PMAdapterAgent": "PMAdapterAgent",
            "PlannerAgent": "PlannerAgent",
            END: END
        },
        "PMAdapterAgent": {
            END: END
        },
        "HumanAssistance": {}  # Will be handled by route_next function
    },
    "entry_point": "ClarifierAgent"
}

