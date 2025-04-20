import json
from typing import Union

import yaml
from pydantic import BaseModel


def prepare_output(data: dict, union=False, indent=4):
    # Convert the data to a JSON string
    json_data = ""
    if union:
        raws = [
            f"""If {k}:\n ```json\n{json.dumps(v, indent=indent)}\n```"""
            for k, v in data.items()
        ]
        json_data = "\n".join(raws)
    else:
        json_data = f"""```json
{json.dumps(data, indent=indent)}
```json"""

    # Format the output
    # output = json_data.replace("{", "{{").replace("}", "}}")
    return f"""Here is an example of the output format you should use:

{json_data}"""


def _convert_basemodel(item):
    """Recursively convert BaseModel instances within lists and dicts."""
    if isinstance(item, BaseModel):
        # Check if the BaseModel has a 'to_structured_string' method
        if hasattr(item, "to_structured_string") and callable(
            getattr(item, "to_structured_string")
        ):
            # Prefer the custom string representation if available
            return item.to_structured_string()
        else:
            # Fallback to model_dump
            return item.model_dump()
    elif isinstance(item, list):
        return [_convert_basemodel(i) for i in item]
    elif isinstance(item, dict):
        return {k: _convert_basemodel(v) for k, v in item.items()}
    else:
        return item


def dumps_to_yaml(data: Union[dict, list, BaseModel], indent=4, add_type=True) -> str:
    # Convert a dictionary, list, or BaseModel to a structured string or YAML string
    processed_data = _convert_basemodel(data)

    # Dump the processed data to YAML
    # Note: If a BaseModel had a to_structured_string method,
    # it would have returned a string directly from _convert_basemodel.
    # Otherwise, we dump the potentially modified dict/list structure.
    if isinstance(processed_data, str):
        # If _convert_basemodel returned a string (from to_structured_string), return it directly
        output = processed_data
    else:
        # Dump dictionary or list to YAML
        output = yaml.dump(
            processed_data, default_flow_style=False, allow_unicode=True, indent=indent
        )
    if not add_type:
        return output
    if isinstance(data, BaseModel):
        output = (
            "<"
            + data.__class__.__name__
            + ">\n"
            + output
            + "\n</"
            + data.__class__.__name__
            + ">"
        )
    else:
        output = f"<start>\n{output}\n</end>"
    return output
