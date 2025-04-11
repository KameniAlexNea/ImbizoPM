import json
from typing import Any, Dict, List, Literal, Union

from pydantic import BaseModel, Field

from ..base_agent import AgentState, BaseAgent
from ..dtypes.taskifier_types import (
    MissingInfoDetails,
    Task,
    TaskPlan,
    TaskPlanComplete,
    TaskPlanMissingInfo,
)
from .agent_routes import AgentRoute


class Task(BaseModel):
    id: str = Field(description="Unique identifier for the task")
    name: str = Field(description="Brief, descriptive name of the task")
    description: str = Field(
        description="Detailed description of what needs to be done"
    )
    deliverable: str = Field(
        description="Specific deliverable this task contributes to"
    )
    owner_role: str = Field(description="Role responsible for completing this task")
    estimated_effort: Literal["Low", "Medium", "High"] = Field(
        description="Estimated effort required to complete this task"
    )
    epic: str = Field(description="Name of the epic this task belongs to")
    phase: str = Field(description="Phase in which this task is to be executed")
    dependencies: List[str] = Field(
        default_factory=list, description="List of task IDs this task depends on"
    )


class MissingInfoDetails(BaseModel):
    unclear_aspects: List[str] = Field(
        default_factory=list,
        description="Key points that are unclear and block task definition",
    )
    questions: List[str] = Field(
        default_factory=list,
        description="Questions that must be answered to clarify the scope",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Concrete suggestions to resolve ambiguity or missing details",
    )


class TaskPlanComplete(BaseModel):
    tasks: List[Task] = Field(
        default_factory=list, description="List of well-defined tasks"
    )
    missing_info: Literal[False] = Field(
        default=False,
        description="Flag indicating that no critical information is missing",
    )
    missing_info_details: MissingInfoDetails = Field(
        default_factory=MissingInfoDetails,
        description="Empty structure when no info is missing",
    )


class TaskPlanMissingInfo(BaseModel):
    missing_info_details: MissingInfoDetails = Field(
        description="Details about what information is missing and how to address it"
    )
    missing_info: Literal[True] = Field(
        default=True,
        description="Flag indicating that important task-related information is missing",
    )
    tasks: List[Task] = Field(
        default_factory=list,
        description="Empty list since tasks can’t be defined without resolving issues",
    )


TaskPlan = Union[TaskPlanComplete, TaskPlanMissingInfo]

TASKIFIER_OUTPUT = """### OUTPUT FORMAT:

If enough information is available:
```json
{{
  "tasks": [
    {{
      "id": "T1",
      "name": "Descriptive task name",
      "description": "Detailed description of what needs to be done",
      "deliverable": "Which deliverable this task contributes to",
      "owner_role": "Role responsible for completing this task",
      "dependencies": ["T2", "T3"],
      "estimated_effort": "Low/Medium/High",
      "epic": "Parent epic name",
      "phase": "Phase where this task should be completed"
    }}
    // ... More tasks
  ],
  "missing_info": false,
  "missing_info_details": {{}}
}}
```

If important information is missing:
```json
{{
  "missing_info": true,
  "missing_info_details": {{
    "unclear_aspects": [
      "Specific aspect that prevents task definition",
      "..."
    ],
    "questions": [
      "Specific question that needs answering before tasks can be defined",
      "..."
    ],
    "suggestions": [
      "Concrete suggestion to address the lack of clarity",
      "..."
    ]
  }},
  "tasks": []
}}
```"""

TASKIFIER_PROMPT = f"""You are the **Taskifier Agent**. Your responsibility is to transform a given project plan into a well-structured list of actionable tasks that are easy to assign, track, and complete. Your output must follow the format provided and reflect a clear breakdown of work.

### PROCESS:
Follow these steps carefully to generate the output:

1. **Understand the input**: Analyze the project plan, phases, and epics.
2. **Decompose epics**: Break down each epic into small, actionable, and independent tasks.
3. **Define dependencies**: Identify which tasks depend on others being completed first.
4. **Assign roles**: Choose an appropriate owner role for each task, based on required skills.
5. **Estimate effort**: Label each task as Low, Medium, or High effort based on complexity.
6. **Validate completeness**: Check if the provided input contains enough information to define meaningful tasks. If not, output missing info instead of tasks.


### GUIDELINES:
- Each task must be achievable by **one person in 1-3 working days**.
- Task **names** must be clear and action-oriented.
- Task **descriptions** must precisely explain what is to be done.
- **Dependencies** must form a logical sequence and avoid circularity.
- **Effort estimates** (Low/Medium/High) should reflect **complexity**, not duration alone.
- **Owner roles** should match the expertise required to complete the task.
- If **information is insufficient**, clearly indicate what's missing and provide helpful suggestions/questions.

{TASKIFIER_OUTPUT}"""


class TaskifierAgent(BaseAgent):
    """Agent that produces detailed tasks with owners and dependencies."""

    def __init__(self, llm, use_structured_output: bool = False):
        super().__init__(
            llm,
            AgentRoute.TaskifierAgent,
            TASKIFIER_PROMPT,
            TASKIFIER_OUTPUT,
            TaskPlan if use_structured_output else None,
        )

    def _prepare_input(self, state: AgentState) -> str:
        return f"""Refined idea: {state['idea'].get('refined', '')}
Goals and objectives: {state['goals']}
Constraints: {json.dumps(state.get('constraints', []), indent=2)}
Outcomes: {json.dumps(state.get('outcomes', []), indent=2)}

MVP: {json.dumps(state['scope'].get('mvp', {}), indent=2)}
Phases: {json.dumps(state['plan'].get('phases', []), indent=2)}
Epics: {json.dumps(state['plan'].get('epics', []), indent=2)}

Break into detailed tasks with effort, roles, and dependencies."""

    def _process_result(self, state: AgentState, result: Dict[str, Any]) -> AgentState:
        tasks = result.get("tasks", [])

        # If missing info, store feedback in the tasks structure
        if result.get("missing_info", False) and result.get("missing_info_details"):
            # Create a special task to carry the feedback
            if "warn_errors" not in state:
                state["warn_errors"] = {}
            state["warn_errors"]["missing_info"] = {
                "missing_info_feedback": result.get("missing_info_details")
            }

        state["tasks"] = tasks
        state["next"] = (
            AgentRoute.ClarifierAgent
            if result.get("missing_info", False) or not tasks
            else AgentRoute.TimelineAgent
        )
        state["current"] = AgentRoute.TaskifierAgent
        return state
