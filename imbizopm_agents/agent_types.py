from typing import Any, Dict

from imbizopm_agents.utils import format_project_plan_for_export
from langgraph.graph import END

from .base_agent import AgentState, BaseAgent


class ClarifierAgent(BaseAgent):
    """Agent that refines the idea, extracts goals, scope, and constraints."""

    def __init__(self, llm):
        system_prompt = """You are the Clarifier Agent. Your job is to refine the user's idea and extract clear goals, scope, and constraints.
Analyze the idea thoroughly and identify any ambiguities or vague aspects that need clarification.

Output format:
- Refined idea: A clear statement of the project
- Goals: Key objectives (3-5 bullet points)
- Constraints: Limitations and boundaries (2-4 bullet points)

Your output should be structured as follows:
{{
    "refined_idea": "<refined idea>",
    "goals": ["<goal 1>", "<goal 2>"],
    "constraints": ["<constraint 1>", "<constraint 2>"]
}}"""
        super().__init__(llm, "Clarifier", system_prompt)

    def _prepare_input(self, state: AgentState) -> str:
        """Prepare input for the agent."""
        # Default implementation that can be overridden
        return state["input"]

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        # Extract refined idea, goals and constraints from the agent's response
        # This is a simplified implementation - would need parsing logic
        state["idea"] = {"refined": result.get("refined_idea", "")}
        state["goals"] = result.get("goals", [])
        state["constraints"] = result.get("constraints", [])

        # Default next agent is OutcomeAgent
        state["next"] = "OutcomeAgent"
        return state


class OutcomeAgent(BaseAgent):
    """Agent that defines success metrics and deliverables."""

    def __init__(self, llm):
        system_prompt = """You are the Outcome Agent. Your job is to define clear success metrics and deliverables based on the refined idea and goals.
        
Output format:
- Success metrics: How will we know this project is successful? (3-5 metrics)
- Deliverables: Tangible outputs that will be produced (list each with description)

Your output should be structured as follows:
{{
    "success_metrics": ["<metric 1>", "<metric 2>"],
    "deliverables": [
        {{
            "name": "<deliverable name>",
            "description": "<deliverable description>"
        }},
        ...
    ]
}}"""
        super().__init__(llm, "Outcome", system_prompt)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""
Refined idea: {state['idea'].get('refined', '')}
Goals: {', '.join(state['goals'])}
Constraints: {', '.join(state['constraints'])}

Define the success metrics and deliverables for this project."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["outcomes"] = result.get("success_metrics", [])
        state["deliverables"] = result.get("deliverables", [])

        # Check if outcomes are clear
        if not state["outcomes"]:
            # No Clear Outcome path
            state["next"] = "ClarifierAgent"
        else:
            state["next"] = "PlannerAgent"
        return state


class PlannerAgent(BaseAgent):
    """Agent that breaks the project into phases, epics, and strategies."""

    def __init__(self, llm):
        system_prompt = """You are the Planner Agent. Your job is to break the project into phases, epics, and high-level strategies.
        
Output format:
- Phases: Sequential project stages (with clear goals for each)
- Epics: Major work areas within phases
- Strategies: High-level approaches to execute this plan
- too_vague: Boolean indicating if the plan is too vague

- If the project is too vague, include "too_vague": true
Your output should be structured as follows:
{{too_vague: true}}

- If the project is clear, include "too_vague": false
{{
    "phases": [
        {{
            "name": "<phase name>",
            "description": "<phase description>"
        }},
        ...
    ],
    "epics": [
        {{
            "name": "<epic name>",
            "description": "<epic description>"
        }},
        ...
    ],
    "strategies": [
        {{
            "name": "<strategy name>",
            "description": "<strategy description>"
        }},
        ...
    ],
    "too_vague": false
}}"""
        super().__init__(llm, "Planner", system_prompt)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""
Refined idea: {state['idea'].get('refined', '')}
Goals: {', '.join(state['goals'])}
Constraints: {', '.join(state['constraints'])}
Outcomes: {', '.join(state['outcomes'])}
Deliverables: {', '.join([d.get('name', '') for d in state['deliverables']])}

Create a high-level plan with phases, epics, and strategies."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["plan"] = {
            "phases": result.get("phases", []),
            "epics": result.get("epics", []),
            "strategies": result.get("strategies", []),
        }

        # Check if plan is too vague
        if result.get("too_vague", False):
            # Too Vague path
            state["next"] = "ClarifierAgent"
        else:
            state["next"] = "ScoperAgent"
        return state


class ScoperAgent(BaseAgent):
    """Agent that trims the plan into an MVP and resolves overload."""

    def __init__(self, llm):
        system_prompt = """You are the Scoper Agent. Your job is to trim the plan into a realistic MVP and resolve any scope overload.
        
Output format:
- MVP scope: Minimum viable product definition
- Scope exclusions: What should be explicitly excluded
- Phased approach: How to incrementally deliver value

Your output should be structured as follows:
{{
    "mvp_scope": {{
        "features": ["<feature 1>", "<feature 2>"],
        "user_stories": ["<user story 1>", "<user story 2>"]
    }},
    "scope_exclusions": ["<exclusion 1>", "<exclusion 2>"],
    "phased_approach": [
        {{
            "phase": "<phase name>",
            "description": "<phase description>"
        }},
        ...
    ]
    "overload": false
}}
"""
        super().__init__(llm, "Scoper", system_prompt)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""
Plan Phases: {state['plan'].get('phases', [])}
Plan Epics: {state['plan'].get('epics', [])}
Constraints: {', '.join(state['constraints'])}

Define a realistic MVP scope and resolve any scope overload issues."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["scope"] = {
            "mvp": result.get("mvp_scope", {}),
            "exclusions": result.get("scope_exclusions", []),
            "phased_approach": result.get("phased_approach", []),
        }

        # Check if there's scope overload
        if result.get("overload", False):
            state["next"] = "NegotiatorAgent"
        else:
            state["next"] = "TaskifierAgent"
        return state


class TaskifierAgent(BaseAgent):
    """Agent that produces detailed tasks with owners and dependencies."""

    def __init__(self, llm):
        system_prompt = """You are the Taskifier Agent. Your job is to break down the plan into detailed tasks with owners and dependencies.
        
Output format:
- Tasks: List of tasks with:
    - ID
    - Name
    - Description
    - Owner role
    - Dependencies (IDs of prerequisite tasks)
    - Estimated effort (Low/Medium/High)

Your output should be structured as follows:
{{
  "tasks": [
    {{
      "id": "T1",
      "name": "Set up repo",
      "description": "Initialize Git repository and README",
      "owner_role": "Developer",
      "dependencies": [],
      "estimated_effort": "Low"
    }},
    ...
  ],
  "missing_info": false  // Set to true if you need more context
}}"""
        super().__init__(llm, "Taskifier", system_prompt)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""
MVP Scope: {state['scope'].get('mvp', {})}
Plan Phases: {state['plan'].get('phases', [])}
Plan Epics: {state['plan'].get('epics', [])}

Break down the plan into detailed tasks with owners and dependencies."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["tasks"] = result.get("tasks", [])

        # Check if there's missing information
        if result.get("missing_info", False):
            state["next"] = "ClarifierAgent"
        else:
            state["next"] = "TimelineAgent"
        return state


class TimelineAgent(BaseAgent):
    """Agent that maps tasks to durations and milestones."""

    def __init__(self, llm):
        system_prompt = """You are the Timeline Agent. Your job is to map tasks to durations and create project milestones.
        
Output format:
- Timeline: Tasks with start/end dates or T+X format
- Milestones: Key project checkpoints
- Critical path: Tasks that directly impact project duration

Your output should be structured as follows:
{{
    "task_durations": {
        "T1": {{"start": "T+0", "end": "T+2"}},
        "T2": {{"start": "T+2", "end": "T+4"}}
    },
    "milestones": ["M1: Repo Initialized", "M2: MVP Complete"],
    "critical_path": ["T1", "T2", "T5"]
}}"""
        super().__init__(llm, "Timeline", system_prompt)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""
        Tasks: {state['tasks']}
        
        Create a project timeline with task durations and milestones.
        """

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["timeline"] = {
            "task_durations": result.get("task_durations", {}),
            "milestones": result.get("milestones", []),
            "critical_path": result.get("critical_path", []),
        }

        state["next"] = "RiskAgent"
        return state


class RiskAgent(BaseAgent):
    """Agent that reviews feasibility and spots contradictions."""

    def __init__(self, llm):
        system_prompt = """You are the Risk Agent. Your job is to review the plan for feasibility and spot contradictions or issues.
        
Output format:
- Risks: List of identified risks with:
    - Description
    - Impact (Low/Medium/High)
    - Probability (Low/Medium/High)
    - Mitigation strategy
- Feasibility assessment: Overall evaluation of plan feasibility

Your output should be structured as follows:
{{
  "risks": [
    {{
      "description": "Dependency on external API",
      "impact": "High",
      "probability": "Medium",
      "mitigation_strategy": "Have a fallback mock service"
    }}
  ],
  "feasible": true
}}"""
        super().__init__(llm, "Risk", system_prompt)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""
Plan: {state['plan']}
Scope: {state['scope']}
Tasks: {state['tasks']}
Timeline: {state['timeline']}

Assess the risks and feasibility of this project plan."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        state["risks"] = result.get("risks", [])

        # Check if plan is feasible
        if result.get("feasible", True):
            state["next"] = "ValidatorAgent"
        else:
            # Unfeasible path
            state["next"] = "PlannerAgent"
        return state


class NegotiatorAgent(BaseAgent):
    """Agent that coordinates conflict resolution among agents."""

    def __init__(self, llm):
        system_prompt = """You are the Negotiator Agent. Your job is to coordinate conflict resolution among the other agents.
        
Output format:
- Conflicts: Identified conflicts with suggestions to resolve
- Tradeoffs: Explicit tradeoffs that should be made
- Recommendations: Which parts of the plan should be adjusted

Your output should be structured as follows:
{{
  "conflicts": [
    {{
      "area": "scope",
      "description": "MVP includes too many epics"
    }}
  ],
  "tradeoffs": ["Exclude analytics dashboard from MVP"],
  "recommendations": ["Refactor MVP with more focus"],
  "conflict_area": "scope"
}}
        """
        super().__init__(llm, "Negotiator", system_prompt)

    def _prepare_input(self, state: AgentState) -> str:
        # Identify which aspect has conflicts
        return f"""
Plan: {state['plan']}
Scope: {state['scope']}
Tasks: {state['tasks']}
Risks: {state['risks']}

Resolve conflicts in the current project state."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        # Update state with negotiation results

        # Based on which aspect was negotiated, return to the appropriate agent
        conflict_area = result.get("conflict_area", "")

        if conflict_area == "plan":
            state["next"] = "PlannerAgent"
        elif conflict_area == "scope":
            state["next"] = "ScoperAgent"
        else:
            state["next"] = "PlannerAgent"  # Default

        return state


class ValidatorAgent(BaseAgent):
    """Agent that verifies alignment between idea, plan, and goals."""

    def __init__(self, llm):
        system_prompt = """You are the Validator Agent. Your job is to verify alignment between the original idea, plan, and goals.
        
Output format:
- Alignment check: 
    - Goals alignment (Yes/No for each goal)
    - Constraints respected (Yes/No for each constraint)
    - Outcomes achievable (Yes/No for each outcome)
- Overall validation: Pass/Fail

Your output should be structured as follows:
{{
  "goals_alignment": {{
    "Goal 1": "Yes",
    "Goal 2": "No"
  }},
  "constraints_respected": {{
    "Budget < $10k": "Yes",
    "Team size = 3": "Yes"
  }},
  "outcomes_achievable": {{
    "Outcome 1": "Yes",
    "Outcome 2": "Yes"
  }},
  "overall_validation": "Pass"  // or "Fail"
}}
        """
        super().__init__(llm, "Validator", system_prompt)

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
        system_prompt = """You are the PM Adapter Agent. Your job is to format the final project plan for export to project management tools.
        
Output format:
- JSON structure ready for import into PM tools
- Summary report of the project plan
- Next steps for the project manager

Your output should be structured as follows:
{{
  "executive_summary": "...",  // A short paragraph summarizing the project
  "key_milestones": ["Milestone 1", "Milestone 2", "..."],
  "timeline_overview": "The project will take approximately X weeks/months with key phases including ...",
  "deliverables_summary": ["Deliverable 1", "Deliverable 2", "..."],
  "top_risks": ["Risk 1: ...", "Risk 2: ..."],
  "notes": ["Assumption 1", "Limitation 1"]
}}"""
        super().__init__(llm, "PMAdapter", system_prompt)

    def _prepare_input(self, state: AgentState) -> str:
        return f"""
Project Plan:
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
