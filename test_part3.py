"""
Test Script for Part 3: A2A Coordination with LangGraph
This demonstrates multi-agent coordination using message passing and shared state.

Test Scenarios:
1. Task Allocation: Simple query routed to single agent
2. Negotiation/Escalation: Multiple agents coordinate
3. Multi-Step Coordination: Complex query requiring multiple agents
"""

from agents.router_agent import RouterAgent
from agents.customer_data_agent import CustomerDataAgent
from agents.support_agent import SupportAgent
from coordination.multi_agent_coordinator import MultiAgentCoordinator


def test_scenario_1_task_allocation():
    """
    Scenario 1: Task Allocation
    Query: "Get customer information for ID 5"
    
    Expected A2A Flow:
    1. Router receives query
    2. Router → Data Agent: "Get customer info for ID 5"
    3. Data Agent fetches via MCP (or placeholder)
    4. Data Agent → Router: Returns customer data
    5. Router returns final response
    """
    print("\n" + "-"*80)
    print("SCENARIO 1: TASK ALLOCATION")
    print("-"*80)
    print("Query: 'Get customer information for ID 5'")
    print("\nExpected: Simple routing to Data Agent → fetch data → return")
    print("-"*80)
    
    # Create agents
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Create coordinator (no MCP for now)
    coordinator = MultiAgentCoordinator(router, data_agent, support_agent, mcp_client=None)
    
    # Process query
    result = coordinator.process_query("Get customer information for ID 5")
    
    # Verify
    print("\n[SCENARIO 1 RESULTS]")
    print(f"  Status: {result['status']}")
    print(f"  Agents involved: {len(result['messages'])} messages")
    print(f"  Final response: {result['final_response']}")
    
    return result


def test_scenario_2_negotiation():
    """
    Scenario 2: Negotiation/Escalation
    Query: "I'm customer 123 and need help upgrading my account"
    
    Expected A2A Flow:
    1. Router detects multiple intents (customer data + support)
    2. Router → Data Agent: "Get customer info for ID 123"
    3. Data Agent fetches data
    4. Data Agent → Support Agent: "Here's the customer context"
    5. Support Agent generates upgrade assistance
    6. Router synthesizes final response
    """
    print("\n" + "-"*80)
    print("SCENARIO 2: NEGOTIATION/ESCALATION")
    print("-"*80)
    print("Query: 'I'm customer 123 and need help upgrading my account'")
    print("\nExpected: Router coordinates between Data + Support agents")
    print("-"*80)
    
    # Create agents
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Create coordinator
    coordinator = MultiAgentCoordinator(router, data_agent, support_agent, mcp_client=None)
    
    # Process query
    result = coordinator.process_query("I'm customer 123 and need help upgrading my account")
    
    # Verify
    print("\n[SCENARIO 2 RESULTS]")
    print(f"  Status: {result['status']}")
    print(f"  Coordination steps: {len(result['coordination_history'])}")
    print(f"  Messages exchanged: {len(result['messages'])}")
    print(f"  Final response: {result['final_response']}")
    
    return result


def test_scenario_3_multi_step():
    """
    Scenario 3: Multi-Step Coordination
    Query: "Show me all active customers with open tickets"
    
    Expected A2A Flow:
    1. Router decomposes query into sub-tasks
    2. Router → Data Agent: "Get all active customers"
    3. Data Agent returns customer list
    4. Router → Support Agent: "Get open tickets for these customers"
    5. Support Agent queries tickets
    6. Router synthesizes combined report
    """
    print("\n" + "-"*80)
    print("SCENARIO 3: MULTI-STEP COORDINATION")
    print("-"*80)
    print("Query: 'Show me all active customers with open tickets'")
    print("\nExpected: Complex coordination requiring both agents sequentially")
    print("-"*80)
    
    # Create agents
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Create coordinator
    coordinator = MultiAgentCoordinator(router, data_agent, support_agent, mcp_client=None)
    
    # Process query
    result = coordinator.process_query("Show me all active customers with open tickets")
    
    # Verify
    print("\n[SCENARIO 3 RESULTS]")
    print(f"  Status: {result['status']}")
    print(f"  Coordination steps: {len(result['coordination_history'])}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Final response: {result['final_response']}")
    
    return result


def test_additional_scenarios():
    """
    Additional test cases from assignment requirements.
    """
    print("\n" + "-"*80)
    print("ADDITIONAL TEST SCENARIOS")
    print("-"*80)
    
    # Create agents
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Create coordinator
    coordinator = MultiAgentCoordinator(router, data_agent, support_agent, mcp_client=None)
    
    test_queries = [
        "I've been charged twice, please refund immediately!",
        "Update my email to new@email.com and show my ticket history",
        "I need help with my account, customer ID 12345"
    ]
    
    results = []
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Query: '{query}'")
        
        result = coordinator.process_query(query, verbose=False)
        results.append(result)
        
        print(f"Status: {result['status']}")
        print(f"Messages: {len(result['messages'])}")
        print(f"Response: {result['final_response'][:100]}...")
    
    return results


def demonstrate_graph_structure():
    """
    Show the graph structure visually.
    """
    print("\n" + "-"*80)
    print("GRAPH STRUCTURE DEMONSTRATION")
    print("-"*80)
    
    # Create coordinator
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    coordinator = MultiAgentCoordinator(router, data_agent, support_agent)
    
    # Visualize
    coordinator.visualize_graph()


def main():
    """
    Run all Part 3 tests.
    """
    print("\n" + "="*40)
    print("PART 3: A2A COORDINATION TESTING")
    print("LangGraph-Style Message Passing System")
    print("="*40)
    
    # Show graph structure first
    demonstrate_graph_structure()
    
    # Test the three main scenarios
    print("\n" + "="*80)
    print("RUNNING REQUIRED SCENARIOS")
    print("="*80 + "\n")
    
    scenario1_result = test_scenario_1_task_allocation()
    scenario2_result = test_scenario_2_negotiation()
    scenario3_result = test_scenario_3_multi_step()
    
    # Additional tests
    additional_results = test_additional_scenarios()
    
    # Summary
    print("\n" + "="*80)
    print("PART 3 TESTING COMPLETE")
    print("="*80)
    
    print("\n[SUMMARY]")
    print(f"  > Scenario 1 (Task Allocation): {scenario1_result['status']}")
    print(f"  > Scenario 2 (Negotiation): {scenario2_result['status']}")
    print(f"  > Scenario 3 (Multi-Step): {scenario3_result['status']}")
    print(f"  > Additional tests: {len(additional_results)} completed")
    
    print("\n[KEY FEATURES DEMONSTRATED]")
    print("  - Shared state management (AgentState)")
    print("  - Agent-to-agent message passing")
    print("  - Conditional routing between agents")
    print("  - Multi-step coordination")
    print("  - Task allocation and negotiation")
    
    print("\n[NEXT STEPS]")
    print("  1. Review agent coordination logs above")
    print("  2. Integrate with MCP (see Part 2)")
    print("  3. Run end-to-end tests with real database")
    print("  4. Deploy and test all scenarios")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()