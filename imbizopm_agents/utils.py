from typing import Any, Dict

from llm_output_parser import parse_json


def extract_structured_data(text: str) -> Dict[str, Any]:
    """
    Extract structured data from agent response text.

    Args:
        text: The text output from an agent

    Returns:
        Dict with extracted structured data
    """
    return parse_json(text)


def format_project_plan_for_export(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the entire project plan for export to external tools.

    Args:
        state: Complete state with all project planning data

    Returns:
        Formatted project plan ready for export
    """
    # Creating a standardized export format
    export = {
        "project": {
            "title": state.get("idea", {}).get("refined", "Untitled Project"),
            "description": state.get("idea", {}).get("description", ""),
            "goals": state.get("goals", []),
            "constraints": state.get("constraints", []),
        },
        "success_criteria": {
            "outcomes": state.get("outcomes", []),
            "deliverables": state.get("deliverables", []),
        },
        "plan": {
            "phases": state.get("plan", {}).get("phases", []),
            "epics": state.get("plan", {}).get("epics", []),
            "strategies": state.get("plan", {}).get("strategies", []),
        },
        "scope": {
            "mvp": state.get("scope", {}).get("mvp", {}),
            "exclusions": state.get("scope", {}).get("exclusions", []),
            "phased_approach": state.get("scope", {}).get("phased_approach", []),
        },
        "execution": {
            "tasks": state.get("tasks", []),
            "timeline": state.get("timeline", {}),
            "milestones": state.get("timeline", {}).get("milestones", []),
            "critical_path": state.get("timeline", {}).get("critical_path", []),
        },
        "risk_management": {
            "risks": state.get("risks", []),
            "mitigations": [
                risk.get("mitigation", "") for risk in state.get("risks", [])
            ],
        },
    }

    return export
