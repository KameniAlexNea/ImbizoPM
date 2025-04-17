import gradio as gr
from langchain.chat_models import init_chat_model
from langgraph.graph.graph import CompiledGraph
from loguru import logger

# Imports
from imbizopm_agents.agents.config import AgentRoute
from imbizopm_agents.graph import (
    create_project_planning_graph,
    run_project_planning_graph,
)
from imbizopm_agents.prompts.utils import dumps_to_yaml

# Initialize model and graph
llm = init_chat_model("ollama:cogito:32b")
graph: CompiledGraph = create_project_planning_graph(
    llm, use_checkpointing=True, use_structured_output=False
)

# Agent names to show
TabsName = [
    AgentRoute.ClarifierAgent,
    AgentRoute.PlannerAgent,
    AgentRoute.ScoperAgent,
    AgentRoute.NegotiatorAgent,
    AgentRoute.TaskifierAgent,
    AgentRoute.TimelineAgent,
    AgentRoute.RiskAgent,
    AgentRoute.ValidatorAgent,
    AgentRoute.PMAdapterAgent,
]

supported_names = {
    name for name in dir(AgentRoute) if not name.startswith("__") and name != "END"
}
agent_names = [i for i in TabsName if i in supported_names]

# Create Gradio interface
with gr.Blocks(title="ImbizoPM: Project Planner") as demo:
    gr.Markdown("## 🤖 ImbizoPM - AI-Powered Project Planner")

    with gr.Row():
        input_textbox = gr.Textbox(
            label="💡 Enter Project Idea",
            placeholder="e.g., Build an app for rural education...",
            lines=3,
            scale=4,
        )
        submit_button = gr.Button("🚀 Run Planning", scale=1)

    status_output = gr.Markdown("Waiting for input...")
    route_info_output = gr.Markdown(
        "Execution path will appear here."
    )  # Added route info output

    # Agent output tabs
    md_outputs = {}

    with gr.Tabs():
        for agent_name in agent_names:
            with gr.Tab(label=agent_name):
                md_outputs[agent_name] = gr.Markdown(
                    f"### {agent_name}\nAwaiting result..."
                )

    output_components = [md_outputs[name] for name in agent_names]

    # Processing function
    def process_input(user_input):
        user_input = user_input.strip()
        if not user_input:
            return gr.Error("Input cannot be empty. Please provide a project idea.")
        thread_id = f"run-{hash(user_input)}"
        logger.info(f"Started planning run: {thread_id}")

        initial = {
            status_output: gr.update(value="⏳ Running agent pipeline..."),
            route_info_output: gr.update(
                value="Execution path will appear here."
            ),  # Initialize route info
            **{
                md: gr.update(value=f"### {name}\nProcessing...")
                for name, md in md_outputs.items()
            },
        }
        yield initial

        try:
            updates = {}

            for event in run_project_planning_graph(
                graph,
                user_input=user_input,
                thread_id=thread_id,
                recursion_limit=30,
                print_results=False,
            ):
                # Print backward and forward node names
                backward_node = event.get("backward")
                event.get("forward")

                agent_name = backward_node  # Use the already fetched backward_node
                if agent_name and agent_name in md_outputs:
                    agent_data = event.get(agent_name)
                    if agent_data:
                        formatted = f"### {agent_name}\n```yaml\n{dumps_to_yaml(agent_data)}\n```"
                        updates[md_outputs[agent_name]] = gr.update(value=formatted)

                # Add this for route visualization
                route_info = f"📍 **Executed:** `{event.get('backward', 'N/A')}` → **Next:** `{event.get('forward', 'N/A')}`"
                updates[route_info_output] = gr.update(value=route_info)

                yield updates  # Yield all updates for this step together

            updates[status_output] = gr.update(value="✅ Planning complete!")
            logger.info(f"Finished planning run: {thread_id}")
            yield updates

        except Exception as e:
            logger.error(f"Graph error: {e}", exc_info=True)
            error_updates = {
                status_output: gr.update(value=f"❌ Error occurred: {e}"),
                route_info_output: gr.update(
                    value="Error during execution."
                ),  # Update route info on error
                **{
                    md: gr.update(value=f"### {name}\n❌ Error processing.")
                    for name, md in md_outputs.items()
                },
            }
            yield error_updates

    submit_button.click(
        fn=process_input,
        inputs=[input_textbox],
        outputs=[status_output, route_info_output]
        + list(md_outputs.values()),  # Added route_info_output
    )

# Run
demo.launch()
