"""
LangGraph style coordination engine

1. State: shared data structure that all agents can read/write
2. Nodes: agent functions that process state and return updates
3. Edges: routing logic that determines which agent runs next
4. Graph: orchesrates the execution flow
"""

from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class AgentState:
    #input
    query: str = "" # original user query

    # routing and coordination
    current_agent: str = "router"  # which agent is currently active
    next_agent: Optional[str] = None  # where to route next
    coordination_history: List[Dict] = field(default_factory=list)  # track agent interactions

    # data collected
    customer_data: Optional[Dict] = None # from CUSTOMER DATA agent
    tickets_data: Optional[List] = None  # from SUPPORT agent

    # agent messages
    messages: List[Dict] = field(default_factory=list)  # messages between agents

    # output
    final_response: str = "" # final response to user
    status: str = "in_progress" # in progress, completed, or error

    # metadata
    iteration_count: int = 0  # prevent infinite loops
    max_iterations:    int = 10 # safety limit

    def add_message(self, from_agent: str, to_agent: str, content: str, data: Optional[Dict] = None):
        """
        Adds message to communication log. Thsi is how agents "talk" to each other

        Args:
            from_agent: sending agent name
            to_agent: receiving agent name
            content: message content (human-readable)
            data: optional structureed data being passed
        """

        message = {
            "timestamp": datetime.now().isoformat(),
            "from": from_agent,
            "to": to_agent,
            "content": content,
            "data": data or {}
        }
        self.messages.append(message)

        # also log in coordination history for debugging
        self. coordination_history.append({
            "step": len(self.coordination_history) + 1,
            "action": f"{from_agent} → {to_agent}",
            "message": content
        })

    
    def increment_iteration(self):
        """ track iterations to prevent infinite loop """
        self.iteration_count += 1
        if self.iteration_count >= self.max_iterations:
            self.status = "error"
            self.final_response = "Max coordination steps reached. Please simplify your query"


class GraphCoordinator:
    """
    Main coordinator that manages the agent graph.
    This is like the "stage manager" that decides which agent performs next.
    """

    def __init__(self):
        """ initialize the coordinator """

        # store agent node functions
        self.nodes: Dict[str, Callable] = {}

        # store routing logic (conditional edges)
        self.routing_functions: Dict[str, Callable] = {}

        # execution log
        self.execution_log: List[Dict] = []

    def add_node(self, name: str, func: Callable):
        """ 
        register agent as node in the graph

        Args:
            name: Agent identifier (e.g., "router", "data_agent")
            func: Function that processes state and returns updates
        """
        self.nodes[name] = func
        print(f"     Registered node: {name}")

    def add_conditional_edges(self, from_node: str, routing_func: Callable):
        """ 
        Add conditional routing logic.
        
        Args:
            from_node: Which node these edges come from
            routing_func: Function that takes state and returns next node name
        """
        self.routing_functions[from_node] = routing_func
        print(f"     Registered conditional edges from: {from_node}")


    def route_next(self, state: AgentState) -> Optional[str]:
        """
        Determine which agent should run next based on current state.
        
        Args:
            state: Current agent state
            
        Returns:
            Name of next agent to run, or None if done
        """
        current = state.current_agent
        
        # Check if we have routing logic for current agent
        if current in self.routing_functions:
            next_agent = self.routing_functions[current](state)
            self.log_routing(current, next_agent, state)
            return next_agent
        
        # No routing logic = we're done
        return None

    def log_routing(self, from_agent: str, to_agent: Optional[str], state: AgentState):
        """Log routing decision for debugging."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "from": from_agent,
            "to": to_agent or "END",
            "iteration": state.iteration_count,
            "state_summary": {
                "has_customer_data": state.customer_data is not None,
                "has_tickets": state.tickets_data is not None,
                "message_count": len(state.messages)
            }
        }
        self.execution_log.append(log_entry)
        print(f"\n[ROUTING] {from_agent} → {to_agent or 'END'} (iteration {state.iteration_count})")
    
    def execute(self, initial_state: AgentState) -> AgentState:
        """
        Execute the agent graph starting from initial state.
        
        This is the main execution loop:
        1. Run current agent node
        2. Determine next agent via routing
        3. Repeat until done or max iterations
        
        Args:
            initial_state: Starting state with query
            
        Returns:
            Final state with response
        """
        state = initial_state
        
        print("\n" + "="*60)
        print("STARTING GRAPH EXECUTION")
        print("="*60)
        print(f"Query: {state.query}")
        print(f"Starting agent: {state.current_agent}\n")
        
        while state.status == "in_progress" and state.iteration_count < state.max_iterations:
            state.increment_iteration()
            
            # Get current agent's node function
            current_agent_name = state.current_agent
            if current_agent_name not in self.nodes:
                print(f"[ERROR] Unknown agent '{current_agent_name}'")
                state.status = "error"
                break
            
            node_func = self.nodes[current_agent_name]
            
            # Execute the agent
            print(f"\n[>] Executing: {current_agent_name.upper()}")
            state = node_func(state)
            
            # Check if we're done
            if state.status in ["completed", "error"]:
                break
            
            # Route to next agent
            next_agent = self.route_next(state)
            
            if next_agent is None:
                # No more agents to call - we're done
                state.status = "completed"
                break
            
            # Update current agent for next iteration
            state.current_agent = next_agent
        
        print("\n" + "="*60)
        print("GRAPH EXECUTION COMPLETE")
        print("="*60)
        print(f"Total iterations: {state.iteration_count}")
        print(f"Total messages: {len(state.messages)}")
        print(f"Status: {state.status}")
        
        return state
    
    def print_execution_summary(self, state: AgentState):
        """
        Print a readable summary of the execution.
        Useful for debugging and understanding coordination.
        """
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        
        print(f"\n[Original Query] {state.query}")
        
        print(f"\n[Coordination Steps] ({len(state.coordination_history)}):")
        for step in state.coordination_history:
            print(f"  {step['step']}. {step['action']}: {step['message']}")
        
        print(f"\n[Agent Messages] ({len(state.messages)}):")
        for msg in state.messages:
            print(f"  [{msg['from']} → {msg['to']}] {msg['content']}")
        
        print(f"\n[Final Response]")
        print(f"  {state.final_response}")
        
        print("\n" + "="*60)



