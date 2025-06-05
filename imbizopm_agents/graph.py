from typing import Dict, Optional, Type

from langchain_core.language_models import BaseChatModel
from langchain_core.messages.ai import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from loguru import logger

from .agents.base_agent import AgentState, BaseAgent
from .graph_config import DEFAULT_GRAPH_CONFIG, NodeSuffix


def update_name(name: str):
    if name == END:
        return name
    return name + NodeSuffix


def create_project_planning_graph(
    llm: BaseChatModel,
    graph_config: Optional[Dict[str, Dict]] = DEFAULT_GRAPH_CONFIG,
    use_checkpointing: bool = True,
    use_structured_output: bool = True,
    use_two_step_generation: bool = True,
) -> CompiledGraph:
    """
    Create the project planning graph with all agents and their connections.

    Args:
        llm: The language model to use for all agents
        graph_config: Optional custom configuration for the graph structure
        use_checkpointing: Whether to use memory checkpointing for the graph
        use_structured_output: Whether to use structured output from LLMs
        use_two_step_generation: Whether to use two-step text-then-JSON generation

    Returns:
        CompiledGraph: The configured graph ready to process user requests
    """
    # use_structured_output = False # Force structured output to False for now
    # Use default config if none provided
    config = graph_config

    # Create the graph
    workflow = StateGraph(AgentState)

    # Initialize agents dictionary to store references
    # agents = {}

    # Add all nodes to the graph
    for node_name, node_config in config["nodes"].items():
        # Create and add agent nodes
        agent_class: Type[BaseAgent] = node_config["agent_class"]
        agent = agent_class(
            llm,
            use_structured_output=use_structured_output,
            use_two_step_generation=use_two_step_generation,
        )
        # agents[node_name] = agent
        workflow.add_node(update_name(node_name), agent.run)

    # Define the conditional routing logic
    def route_next(state: AgentState) -> str:
        """Route to the next agent based on the 'next' field in state."""
        if state.get("forward") is None:
            return END
        return update_name(state["forward"])

    # Set entry point
    workflow.set_entry_point(update_name(config["entry_point"]))

    # Connect all nodes with conditional routing
    for node_name, edges in config["edges"].items():
        if len(edges) == 1:
            # Direct connection to the next node
            workflow.add_edge(update_name(node_name), update_name(edges[0]))
        else:
            workflow.add_conditional_edges(
                node_name + NodeSuffix,
                route_next,
                {update_name(k): update_name(v) for k, v in edges.items()},
            )

    # Apply checkpointing if requested
    if use_checkpointing:
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    else:
        return workflow.compile()


def run_project_planning_graph(
    graph: CompiledGraph,
    user_input: str,
    thread_id: str = "default",
    recursion_limit: int = 5,
    print_results: bool = True,
):
    """
    Run the project planning graph with the given user input.

    Args:
        graph: The compiled project planning graph
        user_input: The user's project idea or request
        thread_id: A unique identifier for this conversation thread

    Returns:
        The final state of the graph after processing
    """
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": recursion_limit,
    }

    # Initialize the state with the user input
    initial_state = {
        "input": user_input,
        "messages": [],
        "forward": update_name(DEFAULT_GRAPH_CONFIG["entry_point"]),
        "backward": "",
        "routes": [],
    }

    # Stream the events
    events = graph.stream(
        initial_state,
        config,
        stream_mode="values",
    )

    # results = []
    for event in events:
        yield event
        if print_results:
            messages = event["messages"]
            if messages:
                message: AIMessage = messages[-1]
                logger.info(message.pretty_repr())
            else:
                logger.info(event)
            logger.info(f"Next Direction: {event['forward']}")
            # Store each state update
            # results.append(event)

    # return results
