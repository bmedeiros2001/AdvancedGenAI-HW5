"""
Test script for Part 1 - System Architecture
This demonstrates the agent structure without MCP or A2A yet.
"""

from agents.router_agent import RouterAgent
from agents.customer_data_agent import CustomerDataAgent
from agents.support_agent import SupportAgent


def test_agent_initialization():
    """Test that all agents initialize correctly."""
    print("=" * 60)
    print("TEST 1: Agent Initialization")
    print("=" * 60)
    
    # Create agents
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Register specialists with router
    router.register_specialist(data_agent)
    router.register_specialist(support_agent)
    
    print(f"\n✓ {router.name} initialized")
    print(f"  Capabilities: {router.capabilities}")
    
    print(f"\n✓ {data_agent.name} initialized")
    print(f"  Capabilities: {data_agent.capabilities}")
    print(f"  MCP Tools: {data_agent.mcp_tools}")
    
    print(f"\n✓ {support_agent.name} initialized")
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


def main():
    """Run all tests."""
    print("\n🚀 Testing Part 1: System Architecture\n")
    
    # Test 1: Initialization
    router, data_agent, support_agent = test_agent_initialization()
    
    # Test 2: Intent Analysis
    test_intent_analysis(router)
    
    # Test 3: Routing
    test_routing(router)
    
    print("\n" + "=" * 60)
    print("✅ Part 1 Tests Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Review the agent interaction logs above")
    print("2. Understand how Router analyzes intent and routes queries")
    print("3. Move on to Part 2: MCP Integration")


if __name__ == "__main__":
    main()