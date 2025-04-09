from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from .agent_routes import AgentRoute

RISK_PROMPT = """You are the Risk Agent. Your job is to identify potential risks, assess the project's feasibility, and develop mitigation strategies.

PROCESS:
1. Review the entire project plan, timeline, and tasks
2. Identify potential risks that could impact success
3. Assess the impact and probability of each risk
4. Develop specific mitigation strategies for high-priority risks
5. Evaluate the overall feasibility of the project plan
6. Look for contradictions or unrealistic aspects in the plan

GUIDELINES:
- Consider technical, resource, timeline, external dependency, and stakeholder risks
- Assess impact based on effect on goals, timeline, budget, and quality
- Probability should reflect realistic likelihood based on project context
- Mitigation strategies should be specific and actionable
- Feasibility assessment should consider team capabilities, resources, and constraints
- Identify any assumptions that may impact feasibility

OUTPUT FORMAT:
{{
    "feasible": true,
    "risks": [
        {{
            "description": "Detailed description of the risk",
            "category": "Technical/Resource/Timeline/External/Stakeholder",
            "impact": "High/Medium/Low",
            "probability": "High/Medium/Low",
            "priority": "High/Medium/Low",
            "mitigation_strategy": "Specific actions to reduce risk",
            "contingency_plan": "What to do if the risk materializes"
        }},
        "..."
    ],
    "assumptions": [
        "Critical assumption that impacts project success",
        "..."
    ],
    "feasibility_concerns": [
        {{
            "area": "Specific area of concern",
            "description": "Detailed description of why this is a concern",
            "recommendation": "How to address this concern"
        }},
        "..."
    ]
}}

// Alternative output if project is not feasible:
{{
    "feasible": false,
    "dealbreakers": [
        {{
            "description": "Critical issue that makes the project unfeasible",
            "impact": "Why this is a dealbreaker",
            "potential_solution": "Possible way to address this issue"
        }},
        "..."
    ],
    "risks": [...],
    "assumptions": [...],
    "feasibility_concerns": [...]
}}
"""


class RiskAgent(BaseAgent):
    """Agent that reviews feasibility and spots contradictions."""

    def __init__(self, llm):
        super().__init__(llm, "Risk", RISK_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""Plan: {state.get("plan", {})}
Scope: {state.get("scope", {})}
Tasks: {state.get("tasks", [])}
Timeline: {state.get("timeline", {})}

Assess risks and overall feasibility."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["risks"] = result.get("risks", [])
        state["feasibility"] = result.get("feasible", True)
        state["next"] = (
            AgentRoute.ValidatorAgent
            if result.get("feasible", True)
            else AgentRoute.PlannerAgent
        )
        return state
