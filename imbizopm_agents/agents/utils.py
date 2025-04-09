from typing import Dict, List


def format_list(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def format_named_list(items: List[Dict[str, str]]) -> str:
    return "\n".join(f"- {i.get('name')}: {i.get('description')}" for i in items)
