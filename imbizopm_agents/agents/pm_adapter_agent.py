import json
from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..dtypes.pm_adapter_types import ProjectSummary
from ..prompts.pm_adapter_prompts import (
    get_pm_adapter_output_format,
    get_pm_adapter_prompt,
)
from ..utils import format_project_plan_for_export
from ..agent_routes import AgentRoute

PM_ADAPTER_OUTPUT = get_pm_adapter_output_format()

PM_ADAPTER_PROMPT = get_pm_adapter_prompt()


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
