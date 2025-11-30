"""
Agent graph nodes
These functions wrap our existing agents to work with the graph coordinator.

Each node function:
1. takes AgentState as input
2. executes agent logic
3. updates state with results
4. returns modified state
"""

from typing import Dict, Any
from coordination.graph_coordinator import AgentState

def create_router_node(router_agent, verbose=True):
    """
    Graph node fro the router agent
    
    Router's job in the graph:
    1. analyze query intent
    2. decide which specialist is needed
    3. set next_agent to route to specialist

    Args:
        router_agent: Instance of RouterAgent
        verbose: Whether to print detailed logs
        
    Returns:
        Node function that processes state
    """

    def router_node(state: AgentState) -> AgentState:
        """ router node function """
        if verbose:
            print(f"    -> Analyzing intent...")

        # use router's intent analysis
        intent = router_agent.analyze_intent(state.query)
        if verbose:
            print(f"       Intent: {intent['primary_intent']}")
            print(f"       Required agents: {intent['requires_agents']}")

        # Determine next agent based on intent
        required_agents = intent['requires_agents']

        if not required_agents:
            # end if error
            state.final_response = "I'm not sure I understand. Could you provide more details?"
            state.status = "completed"
            return state
        
        # route to first required agent
        # for complex cases with multiple agents, we'll handle in routing logic
        agent_map = {
            "Customer Data Agent": "data_agent",
            "Support Agent": "support_agent"
        }

        next_agent_name = agent_map.get(required_agents[0])

        if next_agent_name:
            state.next_agent = next_agent_name
            state.add_message(
                from_agent="router",
                to_agent=next_agent_name,
                content=f"Please handle this query: {state.query}",
                data={'intent':intent}
            )
        else:
            state.status="error"
            state.final_response="Could not route query to appropriate agent"

        return state
    return router_node

def create_data_agent_node(data_agent, mcp_client=None, verbose=True):
    """
    Create a graph node for the Customer Data Agent.
    """

    def data_agent_node(state: AgentState) -> AgentState:
        """ data agent node function """

        if verbose:
            print(f"    -> Processing customer data request...")

        # agent.process does MCP calls
        result = data_agent.process(state.query, context=None)

        # Store customer data directly in state
        if result.get("success"):
            if "customer" in result:
                state.customer_data = result["customer"]
                if verbose:
                    print(f"       [+] Retrieved customer ID: {result['customer']['id']}")
            elif "customers" in result:
                state.customer_data = {"customers": result["customers"]}
                if verbose:
                    print(f"       [+] Retrieved {len(result['customers'])} customers")
            if verbose:
                print("           [+] MCP call completed")
        else:
            if verbose:
                print(f"           [!] MCP call failed: {result.get('content', 'Unknown error')}")

        # Add message using the state's method
        state.add_message(
            from_agent="data_agent",
            to_agent="router",
            content=result.get("content", "Data operation completed"),
            data={"success": result.get("success"), "operation": result.get("operation")}
        )

        # Set next agent
        state.next_agent = "router_final"
        
        return state
    
    return data_agent_node




    
def create_support_agent_node(support_agent, mcp_client=None, verbose=True):
    """
    Create a graph node for the Support Agent.
    
    The Support Agent's job in the graph:
    1. Assess priority of issue
    2. Create ticket if needed (via MCP)
    3. Provide support response
    4. Route to completion
    
    Args:
        support_agent: Instance of SupportAgent
        mcp_client: Optional MCP client for making tool calls
        verbose: Whether to print detailed logs
        
    Returns:
        Node function that processes state
    """

    def support_agent_node(state: AgentState) -> AgentState:
        """
        Support Agent node function.
        
        Process flow:
        1. Assess priority
        2. Check if we need customer data
        3. Create ticket if needed
        4. Generate response
        """
        if verbose:
            print(f"    -> Processing support request...")
        query = state.query

        # assess priority
        priority = support_agent.assess_priority(query)
        if verbose:
            print(f"       Priority: {priority}")

        # check if there is customer data
        if not state.customer_data and "customer" in query.lower():
            # We need customer data but don't have it - route to data agent first
            if verbose:
                print(f"       [!] Need customer data, routing to data agent first")
            state.next_agent = "data_agent"
            state.add_message(
                from_agent="support_agent",
                to_agent="data_agent",
                content="I need customer context to handle this support request"
            )
            return state
        
        # create ticket if this is an issue
        ticket_keywords = ["issue", "problem", "error", "bug", "not working", "billing", "help", "support"]
        needs_ticket = any(keyword in query.lower() for keyword in ticket_keywords)

        if needs_ticket and state.customer_data and mcp_client:
            try:
                customer_id = state.customer_data.get("id")
                if customer_id:
                    ticket_result = mcp_client.call_tool("create_ticket", {
                        "customer_id": customer_id,
                        "issue": query,
                        "priority": priority
                    })
                    if verbose:
                        print(f"       [+] Created ticket #{ticket_result.get('ticket_id')} via MCP")
                    state.tickets_data = [ticket_result]
            except Exception as e:
                if verbose:
                    print(f"       [!] Ticket creation failed: {e}")

        
        # Generate support response
        if state.customer_data:
            customer_name = state.customer_data.get("name", "Customer")
            state.final_response = f"Hello {customer_name}, I understand you need help. "
        else:
            state.final_response = "I understand you need help. "
        
        if needs_ticket:
            state.final_response += f"I've created a {priority}-priority ticket for your issue. "
        
        state.final_response += "Our team will assist you shortly."
                          

        # Add message
        state.add_message(
            from_agent="support_agent",
            to_agent="router",
            content="Support response ready",
            data={"priority": priority, "ticket_created": needs_ticket}
        )
        
        # Route to final response synthesis
        state.next_agent = "router_final"
        
        return state
    
    return support_agent_node


def create_router_final_node(router_agent, verbose=True):
    """
    Create final synthesis node for Router.
    
    This node:
    1. Collects all data from specialists
    2. Synthesizes final response
    3. Marks status as completed
    
    Args:
        router_agent: Instance of RouterAgent
        verbose: Whether to print detailed logs
        
    Returns:
        Node function for final synthesis
    """
    
    def router_final_node(state: AgentState) -> AgentState:
        """
        Final synthesis node.
        
        Combines all collected data into final response.
        """
        if verbose:
            print(f"    [*] Synthesizing final response...")
        
        # If we don't have a final response yet, create one
        if not state.final_response:
            # Build response from collected data
            response_parts = []
            
            if state.customer_data:
                if isinstance(state.customer_data, dict):
                    customer_name = state.customer_data.get("name", "Unknown")
                    customer_status = state.customer_data.get("status", "Unknown")
                    response_parts.append(f"Customer: {customer_name} (Status: {customer_status})")
                else:
                    response_parts.append(f"Customer data retrieved: {state.customer_data}")
            
            if state.tickets_data:
                response_parts.append(f"Tickets: {len(state.tickets_data)} found")
            
            if response_parts:
                state.final_response = " | ".join(response_parts)
            else:
                state.final_response = "Query processed successfully"
        
        # Mark as completed
        state.status = "completed"
        state.next_agent = None
        
        if verbose:
            print(f"       [+] Final response ready")
        
        return state
    
    return router_final_node