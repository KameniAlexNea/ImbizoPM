from enum import Enum
from langgraph.graph import END

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
