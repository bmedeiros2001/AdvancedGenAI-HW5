"""
Routing Logic - Conditional Edges
This defines how agents decide where to route next based on state.

Think of this as a decision tree:
- After Router analyzes → route to specialist
- After Data Agent fetches → route to Support or Final
- After Support Agent → route to Final
"""

from coordination.graph_coordinator import AgentState
from typing import Optional


def router_routing(state: AgentState) -> Optional[str]:
    """
    Routing logic after Router Agent.
    
    Decision tree:
    - If next_agent is set → go there
    - If error → end
    - Otherwise → end
    
    Args:
        state: Current agent state
        
    Returns:
        Next agent name or None
    """
    if state.status in ["completed", "error"]:
        return None
    
    # Router sets next_agent explicitly
    return state.next_agent


def data_agent_routing(state: AgentState) -> Optional[str]:
    """
    Routing logic after Customer Data Agent.
    
    Decision tree:
    - If query also needs support → route to support_agent
    - If error → end
    - Otherwise → route to router_final for synthesis
    
    Args:
        state: Current agent state
        
    Returns:
        Next agent name or None
    """
    if state.status in ["completed", "error"]:
        return None
    
    # Data agent sets next_agent based on query needs
    if state.next_agent:
        return state.next_agent
    
    # Default: go to final synthesis
    return "router_final"


def support_agent_routing(state: AgentState) -> Optional[str]:
    """
    Routing logic after Support Agent.
    
    Decision tree:
    - If needs customer data and don't have it → route to data_agent
    - If error → end
    - Otherwise → route to router_final for synthesis
    
    Args:
        state: Current agent state
        
    Returns:
        Next agent name or None
    """
    if state.status in ["completed", "error"]:
        return None
    
    # Support agent might request data agent
    if state.next_agent == "data_agent":
        return "data_agent"
    
    # Otherwise go to final synthesis
    return "router_final"


def router_final_routing(state: AgentState) -> Optional[str]:
    """
    Routing after final Router synthesis.
    
    This is always the end - return None to terminate.
    
    Args:
        state: Current agent state
        
    Returns:
        None (end of graph)
    """
    # Final node - always end
    return None


# Map of agent names to their routing functions
ROUTING_MAP = {
    "router": router_routing,
    "data_agent": data_agent_routing,
    "support_agent": support_agent_routing,
    "router_final": router_final_routing
}