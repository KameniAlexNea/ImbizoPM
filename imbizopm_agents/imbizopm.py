from typing import Any, Dict, Generator, List, Optional, Tuple

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
from imbizopm_agents.project_refined import (
    get_interface as refine_project_idea,
)
from imbizopm_agents.prompts.utils import dumps_to_yaml

# Configuration
DEFAULT_MODEL = "groq:llama3-70b-8192"
LOGO_PATH = "examples/image.png"

# Agent tabs to display in the UI
AGENT_TABS = [
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


class PlannerUI:
    """Handles the UI components and rendering for the project planner."""

    def __init__(self):
        self.agent_outputs = {}
        self.status_output = None
        self.route_info_output = None
        self.message_trace_output = None
        self.supported_agent_names = self._get_supported_agent_names()

    def _get_supported_agent_names(self) -> List[str]:
        """Get the list of supported agent names from AgentRoute."""
        supported_names = {
            name
            for name in dir(AgentRoute)
            if not name.startswith("__") and name != "END"
        }
        return [i for i in AGENT_TABS if i in supported_names]

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface for the project planner."""
        with gr.Blocks(
            title="ImbizoPM: Project Planner", theme=gr.themes.Soft()
        ) as demo:
            self._create_header()
            with gr.Row(equal_height=True):
                with gr.Column(scale=6):
                    input_area = self._create_input_area()
                with gr.Column(scale=3):
                    model_controls = self._create_model_controls()
                with gr.Column(scale=1):
                    self._create_logo_area()

            self.status_output = gr.Markdown(
                "### Status: Ready for input", elem_id="status-area"
            )

            with gr.Accordion("Execution Path", open=False):
                self.route_info_output = gr.Markdown("Execution path will appear here.")

            with gr.Accordion("Message Trace", open=False):
                self.message_trace_output = gr.Code(
                    language="yaml", value="[]", label="Message Trace", lines=10
                )

            self._create_agent_tabs()

            # Connect the submit button to the processing function
            input_area["submit_button"].click(
                fn=self.process_input,
                inputs=[
                    input_area["input_textbox"],
                    model_controls["model_name"],
                    model_controls["api_key"],
                ],
                outputs=[
                    self.status_output,
                    self.route_info_output,
                    self.message_trace_output,
                ]
                + list(self.agent_outputs.values()),
            )

            # Add examples section
            with gr.Accordion("Examples", open=True):
                examples = [
                    [
                        "Build a mobile app for tracking rural education metrics in developing countries"
                    ],
                    [
                        "Create a project management system for distributed teams working on open source software"
                    ],
                    [
                        "Develop a community garden management system with volunteer coordination"
                    ],
                ]
                gr.Examples(
                    examples=examples,
                    inputs=input_area["input_textbox"],
                )

        return demo

    def _create_header(self):
        """Create the header section of the UI."""
        gr.Markdown(
            """
        # 🤖 ImbizoPM - AI-Powered Project Planner
        
        Transform your ideas into structured project plans with AI assistance.
        Each agent in the pipeline contributes a specialized aspect to your plan.
        """
        )

    def _create_input_area(self) -> Dict:
        """Create the input area components."""
        input_textbox = gr.Textbox(
            label="💡 Enter Your Project Idea",
            placeholder="Describe your project idea in detail (e.g., Build an app for rural education...)",
            lines=5,
            scale=4,
            elem_id="project-input",
        )
        submit_button = gr.Button(
            "🚀 Generate Project Plan",
            scale=1,
            variant="primary",
            elem_id="submit-button",
        )

        return {"input_textbox": input_textbox, "submit_button": submit_button}

    def _create_model_controls(self) -> Dict:
        """Create the model configuration controls."""
        model_name = gr.Textbox(
            label="⚙️ AI Model",
            placeholder="e.g., groq:qwen-qwq-32b, ollama:cogito:32b, openai:gpt-4o, anthropic:claude-3-5-sonnet-latest",
            value=DEFAULT_MODEL,
            scale=3,
            elem_id="model-selection",
        )
        api_key = gr.Textbox(
            label="🔑 API Key",
            placeholder="Model provider API key if required",
            type="password",
            scale=2,
            elem_id="api-key",
        )

        return {"model_name": model_name, "api_key": api_key}

    def _create_logo_area(self):
        """Create the logo area of the UI."""
        gr.Image(
            LOGO_PATH,
            height=100,
            label="ImbizoPM Logo",
            show_label=False,
            container=False,
            elem_id="logo-image",
        )

    def _create_agent_tabs(self):
        """Create tabs for each agent's output."""
        with gr.Tabs(elem_id="agent-tabs"):
            for agent_name in self.supported_agent_names:
                with gr.Tab(label=agent_name):
                    self.agent_outputs[agent_name] = gr.Markdown(
                        f"### {agent_name}\n*Results will appear here after processing*",
                        elem_id=f"output-{agent_name}",
                    )

    def process_input(
        self, user_input: str, model_name: str, api_key: str
    ) -> Generator[Dict[Any, Any], None, None]:
        """
        Process the user input and run the project planning pipeline.

        Args:
            user_input: The project idea description
            model_name: The name of the model to use
            api_key: Optional API key for the model

        Yields:
            Dictionary of component updates for Gradio
        """
        # Clean inputs
        user_input = user_input.strip()
        model_name = model_name.strip()

        # Input validation
        validation_result = self._validate_inputs(user_input, model_name)
        if validation_result:
            yield validation_result
            return

        # Initialize process tracking
        thread_id = f"run-{hash(user_input + model_name)}"
        logger.info(f"Started planning run: {thread_id} with model {model_name}")

        # Initialize model and graph
        try:
            llm, graph = self._initialize_model_and_graph(model_name, api_key)
            logger.info(
                f"Initialized model '{model_name}' and graph for run {thread_id}"
            )
        except Exception as e:
            yield self._create_error_state("initialization", str(e))
            return

        # Start processing - initial state update
        current_updates = self._create_processing_state()
        yield current_updates

        # Run the graph and process events
        try:
            yield from self._run_planning_graph(graph, user_input, thread_id)
        except Exception as e:
            logger.error(f"Graph error during run {thread_id}: {e}", exc_info=True)
            yield self._create_error_state("execution", str(e))

    def _validate_inputs(
        self, user_input: str, model_name: str
    ) -> Optional[Dict[Any, Any]]:
        """Validate user inputs and return error state if invalid."""
        if not user_input:
            return self._create_error_state(
                "input", "Input cannot be empty. Please provide a project idea."
            )
        elif not model_name:
            return self._create_error_state(
                "input", "Model name cannot be empty. Please specify a model."
            )
        return None

    def _initialize_model_and_graph(
        self, model_name: str, api_key: str
    ) -> Tuple[Any, CompiledGraph]:
        """Initialize the LLM and planning graph."""
        try:
            # Prepare model initialization
            model_kwargs = {}
            if api_key:
                model_kwargs["api_key"] = api_key

            # Initialize model and graph
            llm = init_chat_model(model_name, **model_kwargs)
            graph = create_project_planning_graph(
                llm,
                use_checkpointing=True,
                use_structured_output=False,
                use_two_step_generation=True,
            )
            return llm, graph
        except ImportError as e:
            error_msg = (
                f"Required package not found: {e}. "
                f"Please install the necessary integration package "
                f"(e.g., `pip install langchain-openai`)."
            )
            logger.error(f"ImportError: {error_msg}", exc_info=True)
            raise ImportError(error_msg)
        except Exception as e:
            logger.error(f"Error initializing model/graph: {e}", exc_info=True)
            raise

    def _create_processing_state(self) -> Dict[Any, Any]:
        """Create the initial processing state updates."""
        return {
            self.status_output: gr.update(
                value="### Status: ⏳ Running agent pipeline..."
            ),
            self.route_info_output: gr.update(value="Execution path starting..."),
            **{
                md: gr.update(value=f"### {name}\n*Processing...*")
                for name, md in self.agent_outputs.items()
            },
            self.message_trace_output: gr.update(value="[]"),
        }

    def _create_error_state(
        self, error_type: str, error_message: str
    ) -> Dict[Any, Any]:
        """Create error state updates."""
        error_header = {
            "input": "❌ Input Error",
            "initialization": "❌ Initialization Error",
            "execution": "❌ Execution Error",
        }.get(error_type, "❌ Error")

        return {
            self.status_output: gr.update(value=f"### {error_header}\n{error_message}"),
            self.route_info_output: gr.update(value=f"Process failed: {error_message}"),
            **{
                md: gr.update(value=f"### {name}\n*{error_header}*\n\n{error_message}")
                for name, md in self.agent_outputs.items()
            },
            self.message_trace_output: gr.update(value="[]"),
        }

    def _run_planning_graph(
        self, graph: CompiledGraph, user_input: str, thread_id: str
    ) -> Generator[Dict[Any, Any], None, None]:
        """Run the planning graph and yield updates."""
        execution_path_history = []
        all_messages_dict = []
        current_updates = self._create_processing_state()

        # Run the graph
        for event in run_project_planning_graph(
            graph,
            user_input=user_input,
            thread_id=thread_id,
            recursion_limit=30,
            print_results=False,
        ):
            # Extract event information
            backward_node = event.get("backward")
            forward_node = event.get("forward")
            messages = event.get("messages", [])

            # Process agent output
            if backward_node and backward_node in self.agent_outputs:
                agent_data = event.get(backward_node)
                if agent_data:
                    formatted = self._format_agent_output(backward_node, agent_data)
                    current_updates[self.agent_outputs[backward_node]] = gr.update(
                        value=formatted
                    )

            # Update execution path
            if backward_node:
                step_info = self._format_execution_step(backward_node, forward_node)
                execution_path_history.append(step_info)
                current_updates[self.route_info_output] = gr.update(
                    value="<br>".join(execution_path_history)
                )

            # Update message trace
            if messages:
                new_message_dicts = [msg.dict() for msg in messages]
                all_messages_dict.extend(new_message_dicts)
                messages_yaml = dumps_to_yaml(all_messages_dict, add_type=False)
                current_updates[self.message_trace_output] = gr.update(
                    value=messages_yaml
                )

            yield current_updates

        # Final success update
        current_updates[self.status_output] = gr.update(
            value="### Status: ✅ Planning complete!"
        )

        logger.info(f"Finished planning run: {thread_id}")
        yield current_updates

    def _format_agent_output(self, agent_name: str, agent_data: Any) -> str:
        """Format agent output for display."""
        return f"### {agent_name}\n\n{dumps_to_yaml(agent_data, add_type=False)}\n"

    def _format_execution_step(
        self, backward_node: str, forward_node: Optional[str]
    ) -> str:
        """Format execution step for display."""
        next_node = forward_node or "END"
        return f"📍 **Executed:** `{backward_node}` → **Next:** `{next_node}`"


def main(share: bool = False, server_name: str = "0.0.0.0", server_port: int = 7860):
    """
    Main function to launch the Gradio interface.

    Args:
        share: Whether to create a public shareable link
        server_name: Server address to bind to
        server_port: Server port to bind to
    """
    # Initialize and create the UI
    planner_ui = PlannerUI()
    planner = planner_ui.create_interface()
    refined = refine_project_idea()

    demo = gr.TabbedInterface(
        [planner, refined],
        ["Project Planner", "Project Idea Refinement"],
        theme=gr.themes.Soft(),
    )

    # Launch the interface
    demo.launch(
        share=share,
        server_name=server_name,
        server_port=server_port,
        favicon_path=LOGO_PATH,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Launch the ImbizoPM Project Planner UI"
    )
    parser.add_argument(
        "--share", action="store_true", help="Create a public shareable link"
    )
    parser.add_argument(
        "--server-name", default="0.0.0.0", help="Server address to bind to"
    )
    parser.add_argument(
        "--server-port", type=int, default=7860, help="Server port to bind to"
    )

    args = parser.parse_args()
    main(args.share, args.server_name, args.server_port)
