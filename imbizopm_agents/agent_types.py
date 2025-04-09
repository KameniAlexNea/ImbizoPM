from typing import Any, Dict

from langgraph.graph import END

from imbizopm_agents.utils import format_project_plan_for_export

from .base_agent import AgentState, BaseAgent
from .prompts import *


def format_list(items: list[str]) -> str:
    return '\n'.join(f"- {item}" for item in items)


def format_named_list(items: list[Dict[str, str]]) -> str:
    return '\n'.join(f"- {i.get('name')}: {i.get('description')}" for i in items)


class ClarifierAgent(BaseAgent):
    """Agent that refines the idea, extracts goals, scope, and constraints."""

    def __init__(self, llm):
        super().__init__(llm, "Clarifier", CLASSIFIER_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        """Prepare input for the agent."""
        prompt_parts = [state["input"]]
        
        # Check for TaskifierAgent feedback
        if state.get("tasks") and state["tasks"] and isinstance(state["tasks"], list) and len(state["tasks"]) > 0:
            if any(task.get("missing_info_feedback") for task in state["tasks"]):
                missing_info = [task.get("missing_info_feedback") for task in state["tasks"] if task.get("missing_info_feedback")]
                prompt_parts.append(f"Taskifier feedback: {missing_info}")
        
        # Check for PlannerAgent feedback
        if state.get("plan") and state["plan"] and state["plan"].get("vague_feedback"):
            prompt_parts.append(f"Planner feedback: {state['plan'].get('vague_feedback')}")
        
        return "\n".join(prompt_parts)

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["idea"] = {"refined": result.get("refined_idea", "")}
        state["goals"] = result.get("goals", [])
        state["constraints"] = result.get("constraints", [])
        state["next"] = "OutcomeAgent"
        return state


class OutcomeAgent(BaseAgent):
    """Agent that defines success metrics and deliverables."""

    def __init__(self, llm):
        super().__init__(llm, "Outcome", OUTCOME_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""Refined idea:
{state['idea'].get('refined', '')}
Goals:
{format_list(state.get('goals', []))}
Constraints:
{format_list(state.get('constraints', []))}

Define success metrics and deliverables."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["outcomes"] = result.get("success_metrics", [])
        state["deliverables"] = result.get("deliverables", [])
        state["next"] = "PlannerAgent" if state["outcomes"] else "ClarifierAgent"
        return state


class PlannerAgent(BaseAgent):
    """Agent that breaks the project into phases, epics, and strategies."""

    def __init__(self, llm):
        super().__init__(llm, "Planner", PLANNER_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        prompt_parts = [f"Refined idea: {state['idea'].get('refined', '')}"]
        
        if state.get("goals"):
            prompt_parts.append(f"Goals:\n{format_list(state.get('goals', []))}")
            
        if state.get("constraints"):
            prompt_parts.append(f"Constraints:\n{format_list(state.get('constraints', []))}")
            
        if state.get("outcomes"):
            prompt_parts.append(f"Outcomes:\n{format_list(state.get('outcomes', []))}")
            
        deliverables = [d.get("name", "") for d in state.get("deliverables", [])]
        if deliverables:
            prompt_parts.append(f"Deliverables:\n{format_list(deliverables)}")
        
        # Check for negotiation details from NegotiatorAgent
        if state.get("scope") and state["scope"].get("negotiation_details"):
            prompt_parts.append(f"Negotiation details:\n{state['scope'].get('negotiation_details')}")
        
        prompt_parts.append("Break into phases, epics, and strategies.")
        
        return "\n".join(prompt_parts)

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["plan"] = {
            "phases": result.get("phases", []),
            "epics": result.get("epics", []),
            "strategies": result.get("strategies", [])
        }
        
        # Store feedback in plan dictionary if too vague
        if result.get("too_vague", False):
            state["plan"]["vague_feedback"] = result.get("vague_details", {})
            
        state["next"] = "ClarifierAgent" if result.get("too_vague", False) else "ScoperAgent"
        return state


class ScoperAgent(BaseAgent):
    """Agent that trims the plan into an MVP and resolves overload."""

    def __init__(self, llm):
        super().__init__(llm, "Scoper", SCOPER_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        prompt_parts = []
        
        if state["plan"].get("phases"):
            prompt_parts.append(f"Phases: {state['plan'].get('phases', [])}")
            
        if state["plan"].get("epics"):
            prompt_parts.append(f"Epics: {state['plan'].get('epics', [])}")
            
        if state.get("constraints"):
            prompt_parts.append(f"Constraints:\n{format_list(state.get('constraints', []))}")
            
        # Check for negotiation details from NegotiatorAgent
        if state.get("scope") and state["scope"].get("negotiation_details"):
            prompt_parts.append(f"Negotiation details:\n{state['scope'].get('negotiation_details')}")
            
        prompt_parts.append("Define MVP scope and resolve overload.")
        
        return "\n".join(prompt_parts)

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["scope"] = {
            "mvp": result.get("mvp_scope", {}),
            "exclusions": result.get("scope_exclusions", []),
            "phased_approach": result.get("phased_approach", [])
        }
        state["next"] = "NegotiatorAgent" if result.get("overload", False) else "TaskifierAgent"
        return state


class TaskifierAgent(BaseAgent):
    """Agent that produces detailed tasks with owners and dependencies."""

    def __init__(self, llm):
        super().__init__(llm, "Taskifier", TASKIFIER_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""MVP: {state['scope'].get('mvp', {})}
Phases: {state['plan'].get('phases', [])}
Epics: {state['plan'].get('epics', [])}

Break into detailed tasks with effort, roles, and dependencies."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        tasks = result.get("tasks", [])
        
        # If missing info, store feedback in the tasks structure
        if result.get("missing_info", False) and result.get("missing_info_details"):
            # Create a special task to carry the feedback
            feedback_task = {"missing_info_feedback": result.get("missing_info_details")}
            tasks.append(feedback_task)
            
        state["tasks"] = tasks
        state["next"] = "ClarifierAgent" if result.get("missing_info", False) else "TimelineAgent"
        return state


class TimelineAgent(BaseAgent):
    """Agent that maps tasks to durations and milestones."""

    def __init__(self, llm):
        super().__init__(llm, "Timeline", TIMELINE_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""Tasks:
{state.get("tasks", [])}

Estimate timeline with milestones and critical path."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["timeline"] = {
            "task_durations": result.get("task_durations", {}),
            "milestones": result.get("milestones", []),
            "critical_path": result.get("critical_path", [])
        }
        state["next"] = "RiskAgent"
        return state


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
        state["next"] = END if result.get("feasible", True) else "ClarifierAgent"
        return state


class NegotiatorAgent(BaseAgent):
    """Agent that coordinates conflict resolution among agents."""

    def __init__(self, llm):
        super().__init__(llm, "Negotiator", NEGOCIATOR_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        # Identify which aspect has conflicts
        return f"""Plan: {state['plan']}
Scope: {state['scope']}
Tasks: {state['tasks']}
Risks: {state['risks']}

Resolve conflicts in the current project state."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        # Store negotiation details in scope dictionary
        if result.get("negotiation_details"):
            if "scope" not in state:
                state["scope"] = {}
            state["scope"]["negotiation_details"] = result.get("negotiation_details")

        # Based on which aspect was negotiated, return to the appropriate agent
        conflict_area = result.get("conflict_area", "")
        state["next"] = "ScoperAgent" if conflict_area == "scope" else "PlannerAgent"
        return state


class ValidatorAgent(BaseAgent):
    """Agent that verifies alignment between idea, plan, and goals."""

    def __init__(self, llm):
        super().__init__(llm, "Validator", VALIDATOR_PROMPT)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""
Original idea: {state['idea'].get('refined', '')}
Goals: {', '.join(state['goals'])}
Constraints: {', '.join(state['constraints'])}
Outcomes: {', '.join(state['outcomes'])}
Plan: {state['plan']}
Scope: {state['scope']}
Tasks: {state['tasks']}

Validate alignment between the idea, goals, and the resulting plan."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["validation"] = {
            "goals_alignment": result.get("goals_alignment", {}),
            "constraints_respected": result.get("constraints_respected", {}),
            "outcomes_achievable": result.get("outcomes_achievable", {}),
            "overall": result.get("overall_validation", False),
        }

        # Check validation result
        if state["validation"]["overall"]:
            # Valid path
            state["next"] = "PMAdapterAgent"
        else:
            # Mismatch path
            state["next"] = "PlannerAgent"
        return state


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
        state["next"] = END
        return state
