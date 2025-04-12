import json
from typing import Any, Dict

from langchain_core.language_models import BaseChatModel

from imbizopm_agents.prompts.utils import dumps_to_yaml

from ..agent_routes import AgentRoute
from ..base_agent import AgentState, BaseAgent
from ..dtypes.clarifier_types import ProjectPlan
from ..prompts.clarifier_prompts import (
    get_clarifier_output_format,
    get_clarifier_prompt,
)


class ClarifierAgent(BaseAgent):
    """Agent that refines the idea, extracts goals, scope, and constraints."""

    def __init__(self, llm: BaseChatModel, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.ClarifierAgent,
            get_clarifier_output_format(),
            get_clarifier_prompt(),
            ProjectPlan if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        """Prepare input for the agent."""
        if state.get("backward") is not None:
            backward = state.get("backward")
            if backward == AgentRoute.OutcomeAgent:  # From outcome agent
                return f"""
idea: {state['input']}

# Previous Outcome Agent
{dumps_to_yaml(state[AgentRoute.OutcomeAgent])}

From the previous refined idea, goals, and constraints, it was not possible to extract clear success_metrics and deliverables. Please clarify the project idea, goals, and constraints.
"""
            elif backward == AgentRoute.PlannerAgent:  # From planner agent
                return f"""
idea: {state['input']}

# Previous Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent])}

# Previous Outcome Agent
{dumps_to_yaml(state[AgentRoute.OutcomeAgent])}

# Previous Planner Agent
{dumps_to_yaml(state[AgentRoute.PlannerAgent])}

From the previous refined idea, goals, constraints, it was not possible to extract clear phases, epics, and strategies. Please clarify the project idea, goals, and constraints.
"""
            elif backward == AgentRoute.TaskifierAgent:
                return f"""
idea: {state['input']}

# Previous Clarifier Agent
{dumps_to_yaml(state[AgentRoute.ClarifierAgent])}

# Previous Outcome Agent
{dumps_to_yaml(state[AgentRoute.OutcomeAgent])}

# Previous Planner Agent
{dumps_to_yaml(state[AgentRoute.PlannerAgent])}

# Taskifier Agent
Missing info: {json.dumps(state['warn_errors'].get('missing_info', {}), indent=2)}

From the previous refined idea, goals, constraints, it was not possible to extract clear tasks. Please clarify the project idea, goals, and constraints.
"""
        prompt_parts = [state["input"]]

        # Check for TaskifierAgent feedback
        if (
            state.get(AgentRoute.TaskifierAgent)
            and state[AgentRoute.TaskifierAgent].result.tasks
            and state[AgentRoute.TaskifierAgent].result.missing_info
        ):
            prompt_parts.append(
                f"Some issues when generating tasks: {dumps_to_yaml(state[AgentRoute.TaskifierAgent].result.missing_info)}"
            )

        return "\n".join(prompt_parts)

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["forward"] = AgentRoute.OutcomeAgent
        state["backward"] = AgentRoute.ClarifierAgent
        return state
