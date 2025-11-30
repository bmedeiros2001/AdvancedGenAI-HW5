"""
Test True A2A Communication (No Shared State)
"""

from agents.router_agent import RouterAgent
from agents.customer_data_agent import CustomerDataAgent
from agents.support_agent import SupportAgent
from coordination.a2a_coordinator import A2ACoordinator

def test_true_a2a():
    """Test true A2A with message passing"""
    
    print("\n" + "="*70)
    print("TESTING TRUE A2A (Message Passing - No Shared State)")
    print("="*70)
    
    # Create agents
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Create A2A coordinator (sets up message bus)
    coordinator = A2ACoordinator(router, data_agent, support_agent, verbose=True)
    
    # Test queries
    queries = [
        "Get customer information for ID 5",
        "I need help with my account, customer ID 1",
        "I'm customer 2 and need help upgrading my account"
    ]
    
    for query in queries:
        result = coordinator.process_query(query)
        
        print(f"\n✅ Final Response: {result['final_response']}")
        print(f"📨 Total messages exchanged: {len(result['messages'])}")

if __name__ == "__main__":
    test_true_a2a()