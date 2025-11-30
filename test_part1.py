"""
Test script for Part 1 - System Architecture
This demonstrates the agent structure without MCP or A2A yet.
"""

from agents.router_agent import RouterAgent
from agents.customer_data_agent import CustomerDataAgent
from agents.support_agent import SupportAgent
from coordination.a2a_coordinator import A2ACoordinator


def test_agent_initialization():
    """Test that all agents initialize correctly."""
    print("=" * 60)
    print("TEST 1: Agent Initialization")
    print("=" * 60)
    
    # Create agents
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Register specialists with router (A2A style - just names)
    router.specialist_agents["Customer Data Agent"] = "Customer Data Agent"
    router.specialist_agents["Support Agent"] = "Support Agent"
    
    print(f"\n[+] {router.name} initialized")
    print(f"  Capabilities: {router.capabilities}")
    
    print(f"\n[+] {data_agent.name} initialized")
    print(f"  Capabilities: {data_agent.capabilities}")
    print(f"  MCP Tools: {data_agent.mcp_tools}")
    
    print(f"\n[+] {support_agent.name} initialized")
    print(f"  Capabilities: {support_agent.capabilities}")
    print(f"  MCP Tools: {support_agent.mcp_tools}")
    
    return router, data_agent, support_agent


def test_intent_analysis(router):
    """Test the Router's intent analysis."""
    print("\n" + "=" * 60)
    print("TEST 2: Intent Analysis")
    print("=" * 60)
    
    test_queries = [
        "Get customer information for ID 12345",
        "I need help with my account",
        "Update my email to new@email.com",
        "I have a billing issue and need a refund",
        "Show me all active customers"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        intent = router.analyze_intent(query)
        print(f"  Primary Intent: {intent['primary_intent']}")
        print(f"  Required Agents: {intent['requires_agents']}")
        print(f"  Complexity: {intent['complexity']}")


def test_routing(router):
    """Test routing queries to specialists."""
    print("\n" + "=" * 60)
    print("TEST 3: Query Routing")
    print("=" * 60)
    
    test_queries = [
        "Get customer information for ID 5",
        "I need help upgrading my account",
        "List all customers"
    ]
    
    for query in test_queries:
        print(f"\nProcessing: '{query}'")
        response = router.process(query)
        print(f"Response: {response['content']}")



def test_a2a_coordination():
    """Test the full A2A coordination flow."""
    print("\n" + "=" * 60)
    print("TEST 4: A2A Coordination")
    print("=" * 60)
    
    # Initialize agents
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Initialize Coordinator (this sets up the MessageBus)
    coordinator = A2ACoordinator(router, data_agent, support_agent, verbose=True)
    
    test_queries = [
        "Get customer information for ID 12345",
        # "I need help with my account" # Uncomment when support agent is fully ready
    ]
    
    for query in test_queries:
        print(f"\nProcessing Query: '{query}'")
        result = coordinator.process_query(query)
        
        print(f"\nFinal Response: {result['final_response']}")
        print(f"Success: {result['success']}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Testing Part 1: System Architecture")
    print("="*60 + "\n")
    
    # Test 1: Initialization
    router, data_agent, support_agent = test_agent_initialization()
    
    # Test 2: Intent Analysis
    test_intent_analysis(router)
    
    # Test 3: Full A2A Coordination
    test_a2a_coordination()
    
    print("\n" + "=" * 60)
    print("Part 1 Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()