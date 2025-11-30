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
from mcp.mcp_client import MCPClient


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
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " SCENARIO 1: TASK ALLOCATION".center(78) + "║")
    print("╚" + "="*78 + "╝")
    print("\n  [Query] 'Get customer information for ID 5'")
    print("  [Expected] Simple routing to Data Agent → fetch data → return\n")
    
    # Create agents silently
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Create coordinator with verbose=False
    coordinator = MultiAgentCoordinator(router, data_agent, support_agent, verbose=False)
    
    # Process query with verbose output
    result = coordinator.process_query("Get customer information for ID 5", verbose=True)
    
    # Verify
    print("\n  ┌─ RESULTS " + "─" * 66 + "┐")
    print(f"  │  Status: {result['status'].upper()}")
    print(f"  │  Coordination Steps: {len(result['coordination_history'])}")
    print(f"  │  Final Response: {result['final_response'][:60]}...")
    print("  └" + "─" * 76 + "┘")
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
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " SCENARIO 2: NEGOTIATION/ESCALATION".center(78) + "║")
    print("╚" + "="*78 + "╝")
    print("\n  [Query] 'I'm customer 1 and need help upgrading my account'")
    print("  [Expected] Router coordinates between Data + Support agents\n")
    
    # Create agents silently
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Create coordinator with verbose=False
    coordinator = MultiAgentCoordinator(router, data_agent, support_agent, verbose=False)
    
    # Process query - use valid customer ID
    result = coordinator.process_query("I'm customer 1 and need help upgrading my account", verbose=True)
    
    # Verify
    print("\n  ┌─ RESULTS " + "─" * 66 + "┐")
    print(f"  │  Status: {result['status'].upper()}")
    print(f"  │  Coordination Steps: {len(result['coordination_history'])}")
    print(f"  │  Messages Exchanged: {len(result['messages'])}")
    print(f"  │  Final Response: {result['final_response'][:60]}...")
    print("  └" + "─" * 76 + "┘")
    
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
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " SCENARIO 3: MULTI-STEP COORDINATION".center(78) + "║")
    print("╚" + "="*78 + "╝")
    print("\n  [Query] 'Show me all active customers with open tickets'")
    print("  [Expected] Complex coordination requiring both agents sequentially\n")
    
    # Create agents silently
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Create coordinator with verbose=False
    coordinator = MultiAgentCoordinator(router, data_agent, support_agent, verbose=False)
    
    # Process query
    result = coordinator.process_query("Show me all active customers with open tickets", verbose=True)
    
    # Verify
    print("\n  ┌─ RESULTS " + "─" * 66 + "┐")
    print(f"  │  Status: {result['status'].upper()}")
    print(f"  │  Coordination Steps: {len(result['coordination_history'])}")
    print(f"  │  Iterations: {result['iterations']}")
    print(f"  │  Final Response: {result['final_response'][:60]}...")
    print("  └" + "─" * 76 + "┘")
    
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

    coordinator = MultiAgentCoordinator(router, data_agent, support_agent, verbose=False)
    
    test_queries = [
        ("Refund Request", "I've been charged twice, please refund immediately!"),
        ("Update Email", "Update my email to new@email.com and show my ticket history for customer 2"),
        ("Account Help", "I need help with my account, customer ID 3")
    ]
    
    results = []
    for i, (name, query) in enumerate(test_queries, 1):
        print(f"  ┌─ Test Case {i}: {name} " + "─" * (55 - len(name)) + "┐")
        print(f"  │  Query: {query[:68]}")
        if len(query) > 68:
            print(f"  │         {query[68:]}")
        
        result = coordinator.process_query(query, verbose=False)
        results.append(result)
        
        print(f"  │  Status: {result['status'].upper()} | Messages: {len(result['messages'])} | Steps: {len(result['coordination_history'])}")
        print(f"  │  Response: {result['final_response'][:62]}...")
        print("  └" + "─" * 76 + "┘\n")
    
    return results


def demonstrate_graph_structure():
    """
    Show the graph structure visually.
    """
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " AGENT GRAPH VISUALIZATION".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    # Create coordinator silently
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    coordinator = MultiAgentCoordinator(router, data_agent, support_agent, verbose=False)
    
    # Visualize
    coordinator.visualize_graph()


def main():
    """
    Run all Part 3 tests.
    """
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " PART 3: A2A COORDINATION TESTING".center(78) + "║")
    print("║" + " LangGraph-Style Message Passing System".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    # Show graph structure first
    demonstrate_graph_structure()
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " RUNNING REQUIRED SCENARIOS".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    scenario1_result = test_scenario_1_task_allocation()
    scenario2_result = test_scenario_2_negotiation()
    scenario3_result = test_scenario_3_multi_step()
    
    # Additional tests
    additional_results = test_additional_scenarios()
    
    # Summary
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " TESTING COMPLETE".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    print("\n  ┏━ SUMMARY " + "━" * 66 + "┓")
    print(f"  ┃  [+] Scenario 1 (Task Allocation): {scenario1_result['status'].upper()}")
    print(f"  ┃  [+] Scenario 2 (Negotiation): {scenario2_result['status'].upper()}")
    print(f"  ┃  [+] Scenario 3 (Multi-Step): {scenario3_result['status'].upper()}")
    print(f"  ┃  [+] Additional tests: {len(additional_results)} completed")
    print("  ┗" + "━" * 76 + "┛")
    
    print("\n  ┏━ KEY FEATURES DEMONSTRATED " + "━" * 48 + "┓")
    print("  ┃  - Shared state management (AgentState)")
    print("  ┃  - Agent-to-agent message passing")
    print("  ┃  - Conditional routing between agents")
    print("  ┃  - Multi-step coordination")
    print("  ┃  - Task allocation and negotiation")
    print("  ┗" + "━" * 76 + "┛")
    
    print("\n  ┏━ NEXT STEPS " + "━" * 63 + "┓")
    print("  ┃  1. Review agent coordination logs above")
    print("  ┃  2. Integrate with MCP (see Part 2)")
    print("  ┃  3. Run end-to-end tests with real database")
    print("  ┃  4. Deploy and test all scenarios")
    print("  ┗" + "━" * 76 + "┛\n")


if __name__ == "__main__":
    main()