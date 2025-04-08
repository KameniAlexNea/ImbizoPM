from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.types import Command, interrupt

from .agent_types import (
    ClarifierAgent,
    NegotiatorAgent,
    OutcomeAgent,
    PlannerAgent,
    PMAdapterAgent,
    RiskAgent,
    ScoperAgent,
    TaskifierAgent,
    TimelineAgent,
    ValidatorAgent,
)
from .base_agent import AgentState


@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]


def create_project_planning_graph(
    llm: BaseChatModel, use_checkpointing: bool = True
) -> CompiledGraph:
    """
    Create the project planning graph with all agents and their connections.

    Args:
        llm: The language model to use for all agents
        use_checkpointing: Whether to use memory checkpointing for the graph

    Returns:
        StateGraph: The configured graph ready to process user requests
    """
    # Create all the agents
    clarifier = ClarifierAgent(llm)
    outcome = OutcomeAgent(llm)
    planner = PlannerAgent(llm)
    scoper = ScoperAgent(llm)
    taskifier = TaskifierAgent(llm)
    risk = RiskAgent(llm)
    timeline = TimelineAgent(llm)
    negotiator = NegotiatorAgent(llm)
    validator = ValidatorAgent(llm)
    pm_adapter = PMAdapterAgent(llm)

    # Create the graph
    workflow = StateGraph(AgentState)

    # Add all agents to the graph
    workflow.add_node("ClarifierAgent", clarifier.run)
    workflow.add_node("OutcomeAgent", outcome.run)
    workflow.add_node("PlannerAgent", planner.run)
    workflow.add_node("ScoperAgent", scoper.run)
    workflow.add_node("TaskifierAgent", taskifier.run)
    workflow.add_node("RiskAgent", risk.run)
    workflow.add_node("TimelineAgent", timeline.run)
    workflow.add_node("NegotiatorAgent", negotiator.run)
    workflow.add_node("ValidatorAgent", validator.run)
    workflow.add_node("PMAdapterAgent", pm_adapter.run)

    # Add human assistance tool node
    workflow.add_node(
        "HumanAssistance",
        lambda state: {
            **state,
            "human_response": human_assistance(
                state.get("human_query", "Need human assistance with project planning")
            ),
            "next": state.get(
                "pending_next", "ClarifierAgent"
            ),  # Return to the agent that requested help
        },
    )

    # Define the conditional routing logic
    def route_next(state: AgentState) -> str:
        """Route to the next agent based on the 'next' field in state."""
        # Check if human assistance is needed
        if state.get("needs_human", False):
            return "HumanAssistance"

        if state.get("next") is None:
            return END
        return state["next"]

    # Set entry point
    workflow.set_entry_point("ClarifierAgent")

    # Connect all agents with conditional routing
    workflow.add_conditional_edges("ClarifierAgent", route_next, {
        "OutcomeAgent": "OutcomeAgent",
        END: END,
    })

    workflow.add_conditional_edges("OutcomeAgent", route_next, {
        "ClarifierAgent": "ClarifierAgent",
        "PlannerAgent": "PlannerAgent",
        END: END,
    })

    workflow.add_conditional_edges("PlannerAgent", route_next, {
        "ScoperAgent": "ScoperAgent",
        END: END,
    })

    workflow.add_conditional_edges("ScoperAgent", route_next, {
        "NegotiatorAgent": "NegotiatorAgent",
        "TaskifierAgent": "TaskifierAgent",
        END: END,
    })

    workflow.add_conditional_edges("TaskifierAgent", route_next, {
        "ClarifierAgent": "ClarifierAgent",
        "TimelineAgent": "TimelineAgent",
        END: END,
    })

    workflow.add_conditional_edges("TimelineAgent", route_next, {
        "RiskAgent": "RiskAgent",
        END: END,
    })

    workflow.add_conditional_edges("RiskAgent", route_next, {
        "ValidatorAgent": "ValidatorAgent",
        "PlannerAgent": "PlannerAgent",
        END: END,
    })

    workflow.add_conditional_edges("NegotiatorAgent", route_next, {
        "PlannerAgent": "PlannerAgent",
        "ScoperAgent": "ScoperAgent",
        END: END,
    })

    workflow.add_conditional_edges("ValidatorAgent", route_next, {
        "PMAdapterAgent": "PMAdapterAgent",
        "PlannerAgent": "PlannerAgent",
        END: END,
    })

    workflow.add_conditional_edges("PMAdapterAgent", route_next, {END: END})

    # Connect human assistance node back to the workflow
    workflow.add_conditional_edges("HumanAssistance", route_next)

    # Apply checkpointing if requested
    if use_checkpointing:
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    else:
        return workflow.compile()


def run_project_planning_graph(graph: CompiledGraph, user_input, thread_id="default"):
    """
    Run the project planning graph with the given user input.

    Args:
        graph: The compiled project planning graph
        user_input: The user's project idea or request
        thread_id: A unique identifier for this conversation thread

    Returns:
        The final state of the graph after processing
    """
    config = {"configurable": {"thread_id": thread_id}}

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
        "next": "ClarifierAgent",
    }

    # Stream the events
    events = graph.stream(
        initial_state,
        config,
        stream_mode="values",
    )

    results = []
    for event in events:
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
