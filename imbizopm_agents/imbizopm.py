import gradio as gr
from langchain.chat_models import init_chat_model
from langgraph.graph.graph import CompiledGraph

from imbizopm_agents.graph import (
    create_project_planning_graph,
    run_project_planning_graph,
)
from imbizopm_agents.prompts.utils import dumps_to_yaml

llm = init_chat_model("ollama:cogito:32b")

graph: CompiledGraph = create_project_planning_graph(
    llm, use_checkpointing=True, use_structured_output=False
)

chat_history = []


def langgraph_chat(user_input, history=None):
    responses = ""
    # Feed input to LangGraph
    for event in run_project_planning_graph(
        graph,
        user_input=user_input,
        thread_id="demo-run-1",  # Adding a unique thread ID for this run
        recursion_limit=30,
        print_results=False,
    ):
        messages = event["messages"]
        if messages:
            curr = event[event["backward"]]
            responses += "\n" + dumps_to_yaml(curr)
            yield responses
        responses += f"\n# Next Direction: {event['forward']}"

    yield responses


iface = gr.ChatInterface(fn=langgraph_chat)
iface.launch()
