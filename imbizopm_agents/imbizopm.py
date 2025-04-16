import gradio as gr
from langchain.chat_models import init_chat_model
from langgraph.graph.graph import CompiledGraph
from loguru import logger

# Import AgentRoute
from imbizopm_agents.agents.config import AgentRoute
from imbizopm_agents.graph import (
    create_project_planning_graph,
    run_project_planning_graph,
)
from imbizopm_agents.prompts.utils import dumps_to_yaml

llm = init_chat_model("ollama:cogito:32b")

graph: CompiledGraph = create_project_planning_graph(
    llm, use_checkpointing=True, use_structured_output=False
)

# Create the Gradio Blocks interface
with gr.Blocks() as demo:
    md_outputs = {}
    agent_names = [
        name
        for name in dir(AgentRoute)
        if not name.startswith("__") and name != "END"
    ]

    with gr.Row():
        input_textbox = gr.Textbox(label="Enter Project Idea", lines=3, scale=4)
        submit_button = gr.Button("Submit", scale=1)  # Add submit button

    with gr.Accordion("Agent Outputs", open=True):
        # Create Markdown outputs for each agent
        cols = 3  # Adjust number of columns as needed
        for i in range(0, len(agent_names), cols):
            with gr.Row():
                for agent_name in agent_names[i : i + cols]:
                    with gr.Column():
                        md_outputs[agent_name] = gr.Markdown(
                            f"### {agent_name}\nWaiting for output...",
                            label=agent_name,
                        )

    # Store Markdown components in a list for easy access in the function
    output_components = [md_outputs[name] for name in agent_names]

    def process_input(user_input):
        # Initialize updates for all markdown outputs to clear them
        initial_updates = {
            md: gr.update(value=f"### {name}\nProcessing...")
            for name, md in md_outputs.items()
        }
        yield initial_updates

        updates = {}
        thread_id = f"run-{hash(user_input)}"  # Simple unique ID per input
        logger.info(f"Starting graph run with thread_id: {thread_id}")

        try:
            # Feed input to LangGraph
            for event in run_project_planning_graph(
                graph,
                user_input=user_input,
                thread_id=thread_id,
                recursion_limit=30,
                print_results=False,
            ):
                agent_name = event.get("backward")
                if agent_name and agent_name in md_outputs:
                    agent_data = event.get(agent_name)
                    if agent_data:
                        formatted_output = (
                            f"### {agent_name}\n```yaml\n{dumps_to_yaml(agent_data)}\n```"
                        )
                        logger.debug(f"Updating Markdown for: {agent_name}")
                        updates[md_outputs[agent_name]] = gr.update(
                            value=formatted_output
                        )
                        yield updates  # Yield intermediate updates
                    else:
                        logger.debug(f"No data found for agent: {agent_name} in event.")

                # Optionally display routing information if needed
                # route_info = f"Next Direction: {event.get('forward', 'N/A')}"
                # updates[some_status_md] = gr.update(value=route_info)
                # yield updates

            logger.info(f"Graph run finished for thread_id: {thread_id}")
            # Final yield with all accumulated updates if needed, though intermediate yields are often better for streaming
            yield updates

        except Exception as e:
            logger.error(f"Error during graph execution: {e}", exc_info=True)
            error_update = {
                md: gr.update(value=f"### {name}\nError occurred.")
                for name, md in md_outputs.items()
            }
            # Add a specific error message display if desired
            # error_update[some_error_md] = gr.update(value=f"Error: {e}")
            yield error_update

    # Attach the process_input function to the button's click event
    submit_button.click(
        fn=process_input, inputs=[input_textbox], outputs=list(md_outputs.values())
    )

# Launch the new interface
demo.launch()
