import json
import os

from langgraph.graph import END

# Import agent classes directly for mapping
from .agents import (
    ClarifierAgent,
    NegotiatorAgent,
    PlannerAgent,
    PMAdapterAgent,
    RiskAgent,
    ScoperAgent,
    TaskifierAgent,
    TimelineAgent,
    ValidatorAgent,
)
from .agents.config import AgentRoute

# Map agent class names (strings) to actual classes
AGENT_CLASSES = {
    AgentRoute.ClarifierAgent: ClarifierAgent,
    AgentRoute.NegotiatorAgent: NegotiatorAgent,
    AgentRoute.PlannerAgent: PlannerAgent,
    AgentRoute.PMAdapterAgent: PMAdapterAgent,
    AgentRoute.RiskAgent: RiskAgent,
    AgentRoute.ScoperAgent: ScoperAgent,
    AgentRoute.TaskifierAgent: TaskifierAgent,
    AgentRoute.TimelineAgent: TimelineAgent,
    AgentRoute.ValidatorAgent: ValidatorAgent,
}

# Load graph configuration from JSON file
config_path = os.path.join(os.path.dirname(__file__), "graph_config.json")
with open(config_path, "r") as f:
    DEFAULT_GRAPH_CONFIG = json.load(f)

# Resolve agent class strings to actual classes
for node_name, node_config in DEFAULT_GRAPH_CONFIG["nodes"].items():
    agent_class_name = node_config.get("agent_class")
    if agent_class_name and agent_class_name in AGENT_CLASSES:
        node_config["agent_class"] = AGENT_CLASSES[agent_class_name]
    else:
        # Handle cases where agent_class might be missing or not found
        # You might want to raise an error or log a warning here
        pass

# Resolve END string in edges
for source_node, destinations in DEFAULT_GRAPH_CONFIG["edges"].items():
    if isinstance(destinations, list):
        DEFAULT_GRAPH_CONFIG["edges"][source_node] = [
            END if dest == "END" else dest for dest in destinations
        ]
    # No change needed for dictionary-based destinations as END is not expected there

NodeSuffix = "Node"
