import json


def prepare_output(data: dict, union=False):
    # Convert the data to a JSON string
    json_data = ""
    if union:
        raws = [
            f"For {k}: \n {json.dumps(v, indent=2)}" for k, v in data.items()
        ]
        json_data = "\n".join(raws)
    else:
        json_data = json.dumps(data, indent=2)

    # Format the output
    output = json_data.replace("{", "{{").replace("}", "}}")
    return f"""Here is an example of the output format you should use:
{output}"""
