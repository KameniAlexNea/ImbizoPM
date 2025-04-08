from typing import Dict, Optional, Type

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.types import Command, interrupt

from .base_agent import AgentState, BaseAgent
from .graph_config import DEFAULT_GRAPH_CONFIG


@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]


def create_project_planning_graph(
    llm: BaseChatModel,
    graph_config: Optional[Dict[str, Dict]] = DEFAULT_GRAPH_CONFIG,
    use_checkpointing: bool = True,
) -> CompiledGraph:
    """
    Create the project planning graph with all agents and their connections.

    Args:
        llm: The language model to use for all agents
        graph_config: Optional custom configuration for the graph structure
        use_checkpointing: Whether to use memory checkpointing for the graph

    Returns:
        CompiledGraph: The configured graph ready to process user requests
    """
    # Use default config if none provided
    config = graph_config

    # Create the graph
    workflow = StateGraph(AgentState)

    # Initialize agents dictionary to store references
    agents = {}

    # Add all nodes to the graph
    for node_name, node_config in config["nodes"].items():
        if node_name == "HumanAssistance":
            # Add human assistance tool node
            workflow.add_node(
                "HumanAssistance",
                lambda state: {
                    **state,
                    "human_response": human_assistance(
                        state.get(
                            "human_query", "Need human assistance with project planning"
                        )
                    ),
                    "next": state.get(
                        "pending_next", config["entry_point"]
                    ),  # Return to the agent that requested help
                },
            )
        elif node_config.get("is_tool", False):
            # Handle other tools if needed
            pass
        else:
            # Create and add agent nodes
            agent_class: Type[BaseAgent] = node_config["agent_class"]
            agent = agent_class(llm)
            agents[node_name] = agent
            workflow.add_node(node_name, agent.run)

    # Define the conditional routing logic
    def route_next(state: AgentState) -> str:
        """Route to the next agent based on the 'next' field in state."""
        # Check if human assistance is needed
        if state.get("needs_human", False):
            state["pending_next"] = state.get("next")
            return "HumanAssistance"

        if state.get("next") is None:
            return END
        return state["next"]

    # Set entry point
    workflow.set_entry_point(config["entry_point"])

    # Connect all nodes with conditional routing
    for node_name, edges in config["edges"].items():
        if node_name == "HumanAssistance":
            # Human assistance routes back based on the pending_next field
            workflow.add_conditional_edges(node_name, route_next)
        else:
            workflow.add_conditional_edges(node_name, route_next, edges)

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
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 5}

    # Initialize the state with the user input
    initial_state = {
        "input": user_input,
        "idea": {"original": user_input},
        "goals": [],
        "constraints": [],
        "outcomes": [],
        "deliverables": [],
        "plan": {},
        "scope": {},
        "tasks": [],
        "timeline": {},
        "risks": [],
        "validation": {},
        "messages": [],
        "next": DEFAULT_GRAPH_CONFIG["entry_point"],  # Use the entry point from config
    }

    # Stream the events
    events = graph.stream(
        initial_state,
        config,
        stream_mode="values",
    )

    results = []
    for event in events:
        print(event["next"])
        messages = event["messages"]
        if messages:
            messages[-1].pretty_print()
        else:
            print(event)
        # Store each state update
        results.append(event)

        # Check if we need human intervention
        snapshot = graph.get_state(config)
        if snapshot.next and snapshot.next[0] == "HumanAssistance":
            print("Human assistance required!")
            query = snapshot.state.get(
                "human_query", "Need human assistance with project planning"
            )
            print(f"Query: {query}")

            # Get actual human input using input()
            human_response = input("Please provide your response: ")

            # Resume the graph with the human response
            human_command = Command(resume={"data": human_response})

            # Continue processing with human input
            continuation = graph.stream(human_command, config, stream_mode="values")
            for cont_event in continuation:
                results.append(cont_event)

    return results
