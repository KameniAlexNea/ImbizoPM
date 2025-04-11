import json
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from ..base_agent import AgentState, BaseAgent
from ..utils import format_project_plan_for_export
from .agent_routes import AgentRoute
from ..dtypes.pm_adapter_types import (
    Milestone,
    PMToolExport,
    ProjectOverview,
    ProjectSummary,
    ResourceRequirement,
)


class ProjectOverview(BaseModel):
    name: str = Field(description="Project name")
    description: str = Field(
        description="Brief description of the project's purpose and scope"
    )
    timeline: str = Field(
        description="Overall timeline of the project, e.g., 'Start date to end date (X weeks/months)'"
    )
    objectives: List[str] = Field(
        default_factory=list, description="List of specific project objectives"
    )
    key_stakeholders: List[str] = Field(
        default_factory=list,
        description="List of key stakeholders or roles involved in the project",
    )


class Milestone(BaseModel):
    name: str = Field(description="Name of the milestone")
    date: str = Field(description="Expected date or timeframe for the milestone")
    deliverables: List[str] = Field(
        default_factory=list,
        description="List of deliverables associated with this milestone",
    )


class ResourceRequirement(BaseModel):
    role: str = Field(
        description="Name or title of the required role (e.g., Developer, QA Analyst)"
    )
    allocation: str = Field(
        description="Level of effort or time commitment (e.g., Full-time, Part-time)"
    )
    skills: List[str] = Field(
        default_factory=list,
        description="List of essential skills required for the role",
    )


class Risk(BaseModel):
    description: str = Field(description="Brief description of the risk")
    impact: Literal["High", "Medium", "Low"] = Field(
        description="Potential impact of the risk on the project"
    )
    mitigation: str = Field(
        description="Proposed strategy or action to mitigate the risk"
    )


class PMToolExport(BaseModel):
    tasks: List[Any] = Field(
        default_factory=list,
        description="List of tasks for project tracking in a PM tool",
    )
    milestones: List[Any] = Field(
        default_factory=list,
        description="List of milestones formatted for PM tool import",
    )
    dependencies: List[Any] = Field(
        default_factory=list, description="List of task dependencies"
    )
    resources: List[Any] = Field(
        default_factory=list,
        description="List of resources (people, tools, etc.) linked to tasks or milestones",
    )


class ProjectSummary(BaseModel):
    executive_summary: str = Field(
        description="Concise overview of the project purpose, approach, and expected outcomes"
    )
    project_overview: ProjectOverview = Field(
        description="General overview including name, description, timeline, objectives, and stakeholders"
    )
    key_milestones: List[Milestone] = Field(
        default_factory=list,
        description="List of important project milestones with expected dates and deliverables",
    )
    resource_requirements: List[ResourceRequirement] = Field(
        default_factory=list,
        description="List of required roles, their allocations, and key skills needed for the project",
    )
    top_risks: List[Risk] = Field(
        default_factory=list,
        description="List of major risks, their impact level, and mitigation strategies",
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Immediate action items or follow-up steps for the project team",
    )
    pm_tool_export: PMToolExport = Field(
        default_factory=PMToolExport,
        description="Exportable structure for project management tools including tasks, milestones, dependencies, and resources",
    )


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

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.PMAdapterAgent,
            PM_ADAPTER_PROMPT,
            PM_ADAPTER_OUTPUT,
            ProjectSummary if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""" Project Description:
- Idea: {json.dumps(state['idea'].get('refined', ''))}
- Goals: {json.dumps(state['goals'])}
- Outcomes: {json.dumps(state['outcomes'])}
- Deliverables: {json.dumps(state['deliverables'])}

# Project Plan:
- Plan: {json.dumps(state['plan'])}
- Scope: {json.dumps(state['scope'])}

# Project Tasks:
- Tasks: {json.dumps(state['tasks'])}

# Project Timeline and Risks:
- Timeline: {json.dumps(state['timeline'])}
- Risks: {json.dumps(state['risks'])}

Format this project plan for export to project management tools. Stricly output only the JSON, to the appropriate format."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["final_output"] = {
            **result,
            "json_export": format_project_plan_for_export(state),
        }

        # This is the final agent, no next state needed
        state["next"] = AgentRoute.END
        state["current"] = AgentRoute.PMAdapterAgent
        return state
