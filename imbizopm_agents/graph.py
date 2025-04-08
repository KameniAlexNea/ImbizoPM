from typing import Dict, Any, TypedDict, List, Optional, Union, Annotated
from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .agent_types import (
    ClarifierAgent,
    OutcomeAgent,
    PlannerAgent,
    ScoperAgent,
    TaskifierAgent,
    RiskAgent,
    TimelineAgent,
    NegotiatorAgent,
    ValidatorAgent,
    PMAdapterAgent
)
from .base_agent import AgentState

def create_project_planning_graph(llm: BaseChatModel) -> StateGraph:
    """
    Create the project planning graph with all agents and their connections.
    
    Args:
        llm: The language model to use for all agents
        
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
    
    # Define the conditional routing logic
    def route_next(state: AgentState) -> str:
        """Route to the next agent based on the 'next' field in state."""
        if state.get("next") is None:
            return END
        return state["next"]
    
    # Set entry point
    workflow.set_entry_point("ClarifierAgent")
    
    # Connect all agents with conditional routing
    workflow.add_conditional_edges(
        "ClarifierAgent",
        route_next
    )
    
    workflow.add_conditional_edges(
        "OutcomeAgent",
        route_next
    )
    
    workflow.add_conditional_edges(
        "PlannerAgent",
        route_next
    )
    
    workflow.add_conditional_edges(
        "ScoperAgent",
        route_next
    )
    
    workflow.add_conditional_edges(
        "TaskifierAgent",
        route_next
    )
    
    workflow.add_conditional_edges(
        "TimelineAgent",
        route_next
    )
    
    workflow.add_conditional_edges(
        "RiskAgent",
        route_next
    )
    
    workflow.add_conditional_edges(
        "NegotiatorAgent",
        route_next
    )
    
    workflow.add_conditional_edges(
        "ValidatorAgent",
        route_next
    )
    
    workflow.add_conditional_edges(
        "PMAdapterAgent",
        route_next
    )
    
    return workflow.compile()
