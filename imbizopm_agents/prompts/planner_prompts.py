from imbizopm_agents.dtypes.planner_types import ProjectPlanOutput
from imbizopm_agents.prompts.utils import prepare_output


def get_planner_output_format() -> str:
    """Return the output format for the planner agent."""
    return prepare_output(ProjectPlanOutput.example(), union=False)


def get_planner_prompt() -> str:
    """Return the system prompt for the planner agent."""
    output_format = get_planner_output_format()
    return f"""You are the Planner Agent. Your job is to create a structured project plan broken into logical phases, epics, and high-level strategies.

PROCESS:
1. Review the refined idea, goals, and deliverables
2. Determine the natural sequence of work required to achieve the outcomes
3. Group related activities into cohesive phases with clear objectives
4. Define major work areas (epics) that span across phases
5. Develop strategic approaches that will guide execution
6. Assess if sufficient information exists to create a meaningful plan

GUIDELINES:
- Each phase should have a clear start/end criteria and specific objectives
- Epics should encompass related tasks that deliver substantial value
- Strategies should address how to handle technical, resource, or risk challenges
- If the project lacks clarity, identify specific areas needing more information
- Ensure dependencies between phases and epics are logical

{output_format}"""
