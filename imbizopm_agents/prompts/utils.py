import json
from typing import Union

import yaml
from pydantic import BaseModel


def prepare_output(data: dict, union=False, indent=4):
    # Convert the data to a JSON string
    json_data = ""
    if union:
        raws = [f"If {k}:\n {json.dumps(v, indent=indent)}" for k, v in data.items()]
        json_data = "\n".join(raws)
    else:
        json_data = json.dumps(data, indent=indent)

    # Format the output
    output = json_data.replace("{", "{{").replace("}", "}}")
    return f"""Here is an example of the output format you should use:
{output}"""


def dumps_to_yaml(data: Union[dict, BaseModel], indent=4) -> str:
    # Convert a dictionary to a YAML string
    if isinstance(data, BaseModel):
        data = data.model_dump()
    return yaml.dump(data, default_flow_style=False, allow_unicode=True, indent=indent)
