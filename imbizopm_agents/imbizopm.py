import os  # Import os to potentially set API keys as environment variables

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


def main():
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

        with gr.Row():
            model_name_input = gr.Textbox(
                label="⚙️ Model Name",
                placeholder="e.g., ollama:cogito:32b, openai:gpt-4o, anthropic:claude-3-5-sonnet-latest",
                value="ollama:cogito:32b",  # Default value
                scale=3,
            )
            api_key_input = gr.Textbox(
                label="🔑 API Key (Optional)",
                placeholder="Enter API key if required by the model provider",
                type="password",
                scale=2,
            )

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

        [md_outputs[name] for name in agent_names]

        # Processing function
        def process_input(user_input, model_name, api_key):  # Added model_name, api_key
            user_input = user_input.strip()
            model_name = model_name.strip()

            # --- Input Validation ---
            error_msg = None
            if not user_input:
                error_msg = "❌ Input cannot be empty. Please provide a project idea."
            elif not model_name:
                error_msg = "❌ Model name cannot be empty."

            if error_msg:
                logger.warning(f"Input validation failed: {error_msg}")
                error_updates = {
                    status_output: gr.update(value=error_msg),
                    route_info_output: gr.update(value="Input Error."),
                    **{
                        md: gr.update(value=f"### {name}\nInput Error.")
                        for name, md in md_outputs.items()
                    },
                }
                yield error_updates  # Yield updates for all components
                return  # Stop processing
            # --- End Input Validation ---

            thread_id = f"run-{hash(user_input + model_name)}"  # Include model in hash
            logger.info(f"Started planning run: {thread_id} with model {model_name}")

            # --- Model and Graph Initialization ---
            try:
                # Prepare kwargs for init_chat_model, handling potential API keys
                model_kwargs = {}
                if api_key:
                    # Heuristic: Set common env vars or pass directly if init_chat_model supports it
                    # This might need adjustment based on specific provider needs in init_chat_model
                    if "openai" in model_name or "azure" in model_name:
                        model_kwargs["api_key"] = api_key
                    elif "anthropic" in model_name:
                        model_kwargs["api_key"] = api_key
                    else:
                        model_kwargs["api_key"] = api_key

                llm = init_chat_model(model_name, **model_kwargs)
                graph: CompiledGraph = create_project_planning_graph(
                    llm, use_checkpointing=True, use_structured_output=False
                )
                logger.info(
                    f"Initialized model '{model_name}' and graph for run {thread_id}"
                )
            except ImportError as e:
                logger.error(f"ImportError initializing model: {e}", exc_info=True)
                error_msg = f"❌ Error: Required package not found. {e}. Please install the necessary integration package (e.g., `pip install langchain-openai`)."
                error_updates = {
                    status_output: gr.update(value=error_msg),
                    route_info_output: gr.update(value="Initialization failed."),
                    **{
                        md: gr.update(value=f"### {name}\nInitialization failed.")
                        for name, md in md_outputs.items()
                    },
                }
                yield error_updates  # Yield updates for all components
                return  # Stop processing
            except Exception as e:
                logger.error(f"Error initializing model/graph: {e}", exc_info=True)
                error_msg = f"❌ Error initializing model or graph: {e}"
                error_updates = {
                    status_output: gr.update(value=error_msg),
                    route_info_output: gr.update(value="Initialization failed."),
                    **{
                        md: gr.update(value=f"### {name}\nInitialization failed.")
                        for name, md in md_outputs.items()
                    },
                }
                yield error_updates  # Yield updates for all components
                return  # Stop processing
            # --- End Initialization ---

            # Initialize the state dictionary that will be yielded
            current_updates = {
                status_output: gr.update(value="⏳ Running agent pipeline..."),
                route_info_output: gr.update(value="Execution path starting..."),
                **{
                    md: gr.update(value=f"### {name}\nProcessing...")
                    for name, md in md_outputs.items()
                },
            }
            yield current_updates  # Yield initial state

            try:
                execution_path_history = []  # Initialize history list

                for event in run_project_planning_graph(
                    graph,
                    user_input=user_input,
                    thread_id=thread_id,
                    recursion_limit=30,
                    print_results=False,  # Keep this false for UI clarity
                ):
                    backward_node = event.get("backward")
                    forward_node = event.get("forward")

                    # Update agent output if available
                    agent_name = backward_node
                    if agent_name and agent_name in md_outputs:
                        agent_data = event.get(agent_name)
                        if agent_data:
                            formatted = f"### {agent_name}\n```yaml\n{dumps_to_yaml(agent_data)}\n```"
                            # Update the specific agent's markdown in current_updates
                            current_updates[md_outputs[agent_name]] = gr.update(
                                value=formatted
                            )

                    # Update execution path history
                    if backward_node:  # Only add steps where a node executed
                        step_info = f"📍 **Executed:** `{backward_node}` → **Next:** `{forward_node or 'END'}`"
                        execution_path_history.append(step_info)
                        # Update the route info markdown in current_updates
                        current_updates[route_info_output] = gr.update(
                            value="<br>".join(execution_path_history)
                        )

                    yield current_updates  # Yield the full state dictionary

                # Final success update
                current_updates[status_output] = gr.update(
                    value="✅ Planning complete!"
                )
                logger.info(f"Finished planning run: {thread_id}")
                yield current_updates  # Yield final state

            except Exception as e:
                logger.error(f"Graph error during run {thread_id}: {e}", exc_info=True)
                # Append error to history if possible
                if "execution_path_history" not in locals():
                    execution_path_history = ["Execution failed before starting."]
                execution_path_history.append(f"❌ **Error:** {e}")
                # Create a full error update dictionary
                final_error_updates = {
                    status_output: gr.update(value=f"❌ Error occurred: {e}"),
                    route_info_output: gr.update(
                        value="<br>".join(
                            execution_path_history
                        )  # Show history up to the error
                    ),
                    **{
                        md: gr.update(value=f"### {name}\n❌ Error processing.")
                        for name, md in md_outputs.items()
                    },
                }
                yield final_error_updates  # Yield full error state

        submit_button.click(
            fn=process_input,
            inputs=[
                input_textbox,
                model_name_input,
                api_key_input,
            ],  # Added model inputs
            outputs=[status_output, route_info_output] + list(md_outputs.values()),
        )
    return demo


# Run

if __name__ == "__main__":
    demo = main()
    demo.launch()
