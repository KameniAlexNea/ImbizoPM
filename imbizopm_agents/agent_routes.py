from langgraph.graph import END

from imbizopm_agents.dtypes.clarifier_types import ProjectPlan
from imbizopm_agents.dtypes.negotiator_types import ConflictResolution
from imbizopm_agents.dtypes.outcome_types import ProjectSuccessCriteria
from imbizopm_agents.dtypes.planner_types import ProjectPlanOutput
from imbizopm_agents.dtypes.pm_adapter_types import ProjectSummary
from imbizopm_agents.dtypes.risk_types import FeasibilityAssessment
from imbizopm_agents.dtypes.scoper_types import ScopeDefinition
from imbizopm_agents.dtypes.taskifier_types import TaskPlan
from imbizopm_agents.dtypes.timeline_types import ProjectTimeline
from imbizopm_agents.dtypes.validator_types import PlanValidation


class AgentRoute:
    ClarifierAgent = "ClarifierAgent"
    OutcomeAgent = "OutcomeAgent"
    PlannerAgent = "PlannerAgent"
    ScoperAgent = "ScoperAgent"
    TaskifierAgent = "TaskifierAgent"
    TimelineAgent = "TimelineAgent"
    RiskAgent = "RiskAgent"
    ValidatorAgent = "ValidatorAgent"
    PMAdapterAgent = "PMAdapterAgent"
    NegotiatorAgent = "NegotiatorAgent"
    END = END

# class AgentStateNames:
#     ClarifierAgent = AgentRoute.ClarifierAgent.lower()
#     OutcomeAgent = AgentRoute.OutcomeAgent.lower()
#     PlannerAgent = AgentRoute.PlannerAgent.lower()
#     ScoperAgent = AgentRoute.ScoperAgent.lower()
#     TaskifierAgent = AgentRoute.TaskifierAgent.lower()
#     TimelineAgent = AgentRoute.TimelineAgent.lower()
#     RiskAgent = AgentRoute.RiskAgent.lower()
#     ValidatorAgent = AgentRoute.ValidatorAgent.lower()
#     PMAdapterAgent = AgentRoute.PMAdapterAgent.lower()
#     NegotiatorAgent = AgentRoute.NegotiatorAgent.lower()

class AgentDtypes:
    ClarifierAgent = ProjectPlan
    OutcomeAgent = ProjectSuccessCriteria
    PlannerAgent = ProjectPlanOutput
    ScoperAgent = ScopeDefinition
    TaskifierAgent = TaskPlan
    TimelineAgent = ProjectTimeline
    RiskAgent = FeasibilityAssessment
    ValidatorAgent = PlanValidation
    PMAdapterAgent = ProjectSummary
    NegotiatorAgent = ConflictResolution
