import typing
from typing import Annotated, Any

from langgraph.graph import END
from langgraph.graph.message import add_messages

from imbizopm_agents.dtypes.clarifier_types import ProjectPlan
from imbizopm_agents.dtypes.negotiator_types import ConflictResolution
from imbizopm_agents.dtypes.planner_types import ProjectPlanOutput
from imbizopm_agents.dtypes.pm_adapter_types import ProjectSummary
from imbizopm_agents.dtypes.risk_types import FeasibilityAssessment
from imbizopm_agents.dtypes.scoper_types import ScopeDefinition
from imbizopm_agents.dtypes.taskifier_types import TaskPlan
from imbizopm_agents.dtypes.timeline_types import ProjectTimeline
from imbizopm_agents.dtypes.validator_types import PlanValidation


class AgentDtypes:
    ClarifierAgent = ProjectPlan
    PlannerAgent = ProjectPlanOutput
    ScoperAgent = ScopeDefinition
    TaskifierAgent = TaskPlan
    TimelineAgent = ProjectTimeline
    RiskAgent = FeasibilityAssessment
    ValidatorAgent = PlanValidation
    PMAdapterAgent = ProjectSummary
    NegotiatorAgent = ConflictResolution


class AgentRoute:
    ClarifierAgent = "ClarifierAgent"
    PlannerAgent = "PlannerAgent"
    ScoperAgent = "ScoperAgent"
    TaskifierAgent = "TaskifierAgent"
    TimelineAgent = "TimelineAgent"
    RiskAgent = "RiskAgent"
    ValidatorAgent = "ValidatorAgent"
    PMAdapterAgent = "PMAdapterAgent"
    NegotiatorAgent = "NegotiatorAgent"
    END = END


# --- Dynamically create AgentState ---

# 1. Define base fields
agent_state_fields = {
    "input": str,
    "start": str,
    "backward": str,
    "forward": str,
    "warn_errors": dict[str, Any],
    "routes": Annotated[list[str], add_messages],
    "messages": Annotated[list[str], add_messages],
}

# 2. Iterate through AgentRoute and add agent-specific fields
for agent_name, _ in AgentRoute.__dict__.items():
    # Filter out non-agent attributes and END
    if not agent_name.startswith("__") and agent_name != "END":
        # Check if the corresponding type exists in AgentDtypes
        if hasattr(AgentDtypes, agent_name):
            agent_type = getattr(AgentDtypes, agent_name)
            agent_state_fields[agent_name] = agent_type
        else:
            # Optional: Handle cases where a route might not have a corresponding dtype
            # For now, we assume all routes in AgentRoute have a corresponding AgentDtypes entry
            pass

# 3. Create the TypedDict dynamically
AgentState = typing.TypedDict("AgentState", agent_state_fields)

# --- End of dynamic creation ---
