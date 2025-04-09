from typing import Any, Dict

from ..base_agent import AgentState, BaseAgent
from ..prompts import PM_ADAPTER_PROMPT
from ..utils import format_project_plan_for_export
from .agent_routes import AgentRoute

class PMAdapterAgent(BaseAgent):
    """Agent that formats and exports the project plan for external tools."""

    def __init__(self, llm):
        super().__init__(llm, "PMAdapter", PM_ADAPTER_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""Project Plan:
- Idea: {state['idea'].get('refined', '')}
- Goals: {', '.join(state['goals'])}
- Outcomes: {', '.join(state['outcomes'])}
- Deliverables: {state['deliverables']}
- Plan: {state['plan']}
- Scope: {state['scope']}
- Tasks: {state['tasks']}
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
        return state
