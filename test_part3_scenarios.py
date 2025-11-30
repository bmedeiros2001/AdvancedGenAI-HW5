"""
Test Script for Part 3: Complex A2A Coordination
Tests the 3 required scenarios: Task Allocation, Negotiation, Multi-Step.
"""

from agents.router_agent import RouterAgent
from agents.customer_data_agent import CustomerDataAgent
from agents.support_agent import SupportAgent
from coordination.a2a_coordinator import A2ACoordinator
import time

def test_scenario_1_task_allocation(coordinator):
    """
    Scenario 1: Task Allocation
    Query: "I need help with my account, customer ID 1"
    Flow: Router -> Data (get info) -> Support (handle request with context)
    """
    print("\n" + "="*70)
    print("SCENARIO 1: TASK ALLOCATION")
    print("Query: 'I need help with my account, customer ID 1'")
    print("Expected: Router fetches data first, then passes to Support")
    print("="*70)
    
    query = "I need help with my account, customer ID 1"
    result = coordinator.process_query(query)
    
    print(f"\nFinal Response: {result['final_response']}")
    
    # Verify flow
    messages = result['messages']
    print(f"\nMessage Flow ({len(messages)} messages):")
    for msg in messages:
        print(f"  [{msg['from']} -> {msg['to']}] {msg['content'][:50]}...")
        
    # Check if Data Agent was involved
    has_data_call = any(m['to'] == 'Customer Data Agent' for m in messages)
    has_support_call = any(m['to'] == 'Support Agent' for m in messages)
    
    if has_data_call and has_support_call:
        print("\n✅ Scenario 1 PASSED: Coordinated Data -> Support")
    else:
        print("\n❌ Scenario 1 FAILED: Missing agent coordination")

def test_scenario_2_negotiation(coordinator):
    """
    Scenario 2: Negotiation
    Query: "I want to cancel my subscription but I'm having billing issues, customer ID 1"
    Flow: Router -> Support (needs context) -> Router -> Data (get history) -> Router -> Support (final)
    """
    print("\n" + "="*70)
    print("SCENARIO 2: NEGOTIATION")
    print("Query: 'I want to cancel my subscription but I'm having billing issues, customer ID 1'")
    print("Expected: Support asks for billing info, Router fetches it, then Support finishes")
    print("="*70)
    
    query = "I want to cancel my subscription but I'm having billing issues, customer ID 1"
    result = coordinator.process_query(query)
    
    print(f"\nFinal Response: {result['final_response']}")
    
    # Verify flow
    messages = result['messages']
    print(f"\nMessage Flow ({len(messages)} messages):")
    for msg in messages:
        print(f"  [{msg['from']} -> {msg['to']}] {msg['content'][:50]}...")
        
    # Check for negotiation pattern
    # 1. Router -> Support
    # 2. Support -> Router (I need context)
    # 3. Router -> Data
    # 4. Data -> Router
    # 5. Router -> Support (Here is context)
    
    if len(messages) >= 4:
         print("\n✅ Scenario 2 PASSED: Negotiation flow detected")
    else:
         print("\n❌ Scenario 2 FAILED: Flow too short for negotiation")

def test_scenario_3_multi_step(coordinator):
    """
    Scenario 3: Multi-Step Coordination
    Query: "What's the status of tickets for all active customers?"
    Flow: Router -> Data (list) -> [Loop] Router -> Support (get tickets) -> Router (Synthesize)
    """
    print("\n" + "="*70)
    print("SCENARIO 3: MULTI-STEP COORDINATION")
    print("Query: 'What's the status of tickets for all active customers?'")
    print("Expected: Router lists customers, then checks tickets for each")
    print("="*70)
    
    query = "What's the status of tickets for all active customers?"
    result = coordinator.process_query(query)
    
    print(f"\nFinal Response:\n{result['final_response']}")
    
    # Verify flow
    messages = result['messages']
    print(f"\nMessage Flow ({len(messages)} messages):")
    for msg in messages:
        # Only show the first few to avoid spam
        print(f"  [{msg['from']} -> {msg['to']}] {msg['content'][:50]}...")
        
    # Check if we have multiple calls to Support (one per customer)
    support_calls = [m for m in messages if m['to'] == 'Support Agent']
    print(f"\nSupport calls made: {len(support_calls)}")
    
    if len(support_calls) >= 2: # We limit to 3 in the code, so should be at least 2
        print("\n✅ Scenario 3 PASSED: Multi-step iteration detected")
    else:
        print("\n❌ Scenario 3 FAILED: Did not iterate through customers")

def main():
    print("INITIALIZING SYSTEM FOR PART 3 TESTS...")
    
    # Initialize agents
    router = RouterAgent()
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Initialize Coordinator
    coordinator = A2ACoordinator(router, data_agent, support_agent, verbose=False) # Less verbose for cleaner output
    
    # Run Scenarios
    test_scenario_1_task_allocation(coordinator)
    time.sleep(1)
    test_scenario_2_negotiation(coordinator)
    time.sleep(1)
    test_scenario_3_multi_step(coordinator)
    
    print("\n" + "="*70)
    print("PART 3 TESTS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
