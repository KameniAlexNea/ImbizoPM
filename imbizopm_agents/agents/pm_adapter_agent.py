from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..utils import format_project_plan_for_export
from .agent_routes import AgentRoute

PM_ADAPTER_OUTPUT = """OUTPUT FORMAT:
{{
    "executive_summary": "Concise overview of the project purpose, approach, and expected outcomes",
    "project_overview": {{
        "name": "Project name",
        "description": "Project description",
        "objectives": ["Objective 1", "..."],
        "key_stakeholders": ["Stakeholder role 1", "..."],
        "timeline": "Start date to end date (X weeks/months)"
    }},
    "key_milestones": [
        {{
            "name": "Milestone name",
            "date": "Expected date/timeframe",
            "deliverables": ["Associated deliverable", "..."]
        }},
        "..."
    ],
    "resource_requirements": [
        {{
            "role": "Required role",
            "skills": ["Required skill", "..."],
            "allocation": "Full-time/Part-time/etc."
        }},
        "..."
    ],
    "top_risks": [
        {{
            "description": "Risk description",
            "impact": "High/Medium/Low",
            "mitigation": "Mitigation strategy"
        }},
        "..."
    ],
    "next_steps": [
        "Immediate action item for project manager",
        "..."
    ],
    "pm_tool_export": {{
        "tasks": [...],
        "milestones": [...],
        "dependencies": [...],
        "resources": [...]
    }}
}}"""

PM_ADAPTER_PROMPT = f"""You are the PM Adapter Agent. Your job is to package the final project plan into a format suitable for project management tools and provide an executive summary for stakeholders.

PROCESS:
1. Consolidate all components of the project plan
2. Format the plan for compatibility with PM tools
3. Create a concise executive summary for stakeholders
4. Highlight key milestones, risks, and deliverables
5. Provide guidance on next steps for implementation

GUIDELINES:
- The executive summary should be brief but comprehensive
- Focus on information most relevant to project sponsors and stakeholders
- Include critical dates, resource needs, and key decision points
- Highlight top risks and their mitigation strategies
- Structure export format to minimize manual reformatting
- Provide actionable next steps for the project manager

{PM_ADAPTER_OUTPUT}"""


class PMAdapterAgent(BaseAgent):
    """Agent that formats and exports the project plan for external tools."""

    def __init__(self, llm):
        super().__init__(
            llm, AgentRoute.PMAdapterAgent, PM_ADAPTER_PROMPT, PM_ADAPTER_OUTPUT
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""" Project Description:
- Idea: {state['idea'].get('refined', '')}
- Goals: {', '.join(state['goals'])}
- Outcomes: {', '.join(state['outcomes'])}
- Deliverables: {state['deliverables']}

# Project Plan:
- Plan: {state['plan']}
- Scope: {state['scope']}

# Project Tasks:
- Tasks: {state['tasks']}

# Project Timeline and Risks:
- Timeline: {state['timeline']}
- Risks: {state['risks']}

Format this project plan for export to project management tools."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["final_output"] = {
            **result,
            "json_export": format_project_plan_for_export(state),
        }

        # This is the final agent, no next state needed
        state["next"] = AgentRoute.END
        state["current"] = AgentRoute.PMAdapterAgent
        return state
