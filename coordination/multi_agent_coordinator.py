"""
Multi-Agent Coordinator
This is the main entry point that sets up the LangGraph-style coordination system.

It:
1. Creates the graph coordinator
2. Registers all agent nodes
3. Sets up conditional routing
4. Provides easy interface for processing queries
"""

from typing import Dict, Any, Optional
from coordination.graph_coordinator import GraphCoordinator, AgentState
from coordination.agent_nodes import (
    create_router_node,
    create_data_agent_node,
    create_support_agent_node,
    create_router_final_node
)
from coordination.routing_logic import ROUTING_MAP


class MultiAgentCoordinator:
    """
    Main coordinator that manages multi-agent communication.
    
    This is what you'll use in your tests:
    coordinator = MultiAgentCoordinator(router, data_agent, support_agent, mcp_client)
    result = coordinator.process_query("Get customer info for ID 5")
    """
    
    def __init__(self, router_agent, data_agent, support_agent, mcp_client=None):
        """
        Initialize the multi-agent coordinator.
        
        Args:
            router_agent: Router agent instance
            data_agent: Customer data agent instance
            support_agent: Support agent instance
            mcp_client: Optional MCP client for tool calls
        """
        self.router_agent = router_agent
        self.data_agent = data_agent
        self.support_agent = support_agent
        self.mcp_client = mcp_client
        
        # Create the graph coordinator
        self.graph = GraphCoordinator()
        
        # Set up the graph
        self._setup_graph()
        
        print("\n[+] Multi-Agent Coordinator initialized")
        print(f"   Agents: Router, Data Agent, Support Agent")
        print(f"   MCP: {'Connected' if mcp_client else 'Not connected (using placeholders)'}\n")
    
    def _setup_graph(self):
        """
        Set up the agent graph structure.
        
        Graph structure:
        
        START
          ↓
        [Router] ←──────┐
          ↓              │
        (routing)        │
          ↓              │
        [Data Agent] ←───┤
          ↓              │
        [Support Agent] ─┤
          ↓              │
        [Router Final] ──┘
          ↓
        END
        
        """
        print("[*] Setting up agent graph...")
        
        # Create node functions (these wrap our agents)
        router_node = create_router_node(self.router_agent)
        data_node = create_data_agent_node(self.data_agent, self.mcp_client)
        support_node = create_support_agent_node(self.support_agent, self.mcp_client)
        final_node = create_router_final_node(self.router_agent)
        
        # Register nodes with graph
        self.graph.add_node("router", router_node)
        self.graph.add_node("data_agent", data_node)
        self.graph.add_node("support_agent", support_node)
        self.graph.add_node("router_final", final_node)
        
        # Add conditional routing for each node
        for agent_name, routing_func in ROUTING_MAP.items():
            self.graph.add_conditional_edges(agent_name, routing_func)
        
        print("[+] Graph setup complete\n")
    
    def process_query(self, query: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Process a user query through the multi-agent system.
        
        This is the main method you'll call in your tests.
        
        Args:
            query: User's query string
            verbose: Whether to print execution summary
            
        Returns:
            Dictionary with:
            - final_response: The response to show the user
            - messages: All agent-to-agent messages
            - coordination_history: Step-by-step coordination log
            - customer_data: Any customer data retrieved
            - status: completed/error
        """
        # Create initial state
        initial_state = AgentState(
            query=query,
            current_agent="router",  # Always start with router
            status="in_progress"
        )
        
        # Execute the graph
        final_state = self.graph.execute(initial_state)
        
        # Print summary if verbose
        if verbose:
            self.graph.print_execution_summary(final_state)
        
        # Return result as dictionary
        return {
            "query": query,
            "final_response": final_state.final_response,
            "status": final_state.status,
            "messages": final_state.messages,
            "coordination_history": final_state.coordination_history,
            "customer_data": final_state.customer_data,
            "tickets_data": final_state.tickets_data,
            "iterations": final_state.iteration_count
        }
    
    def process_batch(self, queries: list[str]) -> list[Dict[str, Any]]:
        """
        Process multiple queries in batch.
        
        Args:
            queries: List of query strings
            
        Returns:
            List of results, one per query
        """
        results = []
        
        for i, query in enumerate(queries, 1):
            print(f"\n{'='*60}")
            print(f"PROCESSING QUERY {i}/{len(queries)}")
            print(f"{'='*60}\n")
            
            result = self.process_query(query, verbose=True)
            results.append(result)
        
        return results
    
    def visualize_graph(self):
        """
        Print a visual representation of the agent graph.
        Useful for understanding the coordination structure.
        """
        print("\n" + "="*60)
        print("         AGENT GRAPH VISUALIZATION")
        print("="*60)
        print("""
        START (User Query)
          ↓
        ┌─────────────────┐
        │  ROUTER AGENT   │  ← Entry point
        │  (Orchestrator) │    Analyzes intent
        └────────┬────────┘    Routes to specialist
                 ↓
        ┌────────┴────────┐
        │  Conditional    │
        │  Routing        │
        └────┬──────┬─────┘
             ↓      ↓
    ┌────────────┐ ┌────────────┐
    │ DATA AGENT │ │   SUPPORT  │
    │ (Specialist│ │   AGENT    │
    │  Database) │ │ (Specialist│
    └─────┬──────┘ └──────┬─────┘
          │               │
          └───────┬───────┘
                  ↓
        ┌─────────────────┐
        │  ROUTER FINAL   │  ← Synthesis
        │  (Synthesizer)  │    Combines results
        └────────┬────────┘
                 ↓
              END (Response)
        
        KEY:
        - Router: Analyzes intent, coordinates agents
        - Data Agent: Accesses customer database via MCP
        - Support Agent: Handles tickets and support
        - Router Final: Synthesizes final response
        """)
        print("="*60 + "\n")