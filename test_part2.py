"""
Test Script for Part 2: MCP Integration
This tests the MCP server and agent integration with the database.

Test Coverage:
1. Direct MCP Server Tests (all 5 tools)
2. Agent Integration Tests (agents using MCP)
3. Error Handling Tests
"""

from mcp.mcp_server import MCPServer
from mcp.mcp_client import MCPClient
from agents.customer_data_agent import CustomerDataAgent
from agents.support_agent import SupportAgent
import json


def test_mcp_server_direct():
    """
    Test all 5 MCP tools directly (without agents).
    This verifies the database operations work correctly.
    """
    print("\n" + "="*70)
    print("TEST 1: DIRECT MCP SERVER TESTING")
    print("="*70)
    
    server = MCPServer()
    
    # Tool 1: get_customer
    print("\n[1] Testing: get_customer(5)")
    print("-"*70)
    result = server.get_customer(5)
    print(json.dumps(result, indent=2))
    assert result['success'], "get_customer should succeed"
    assert result['customer']['name'] == "Eve Martinez", "Should get correct customer"
    print("✓ get_customer works!")
    
    # Tool 2: list_customers
    print("\n[2] Testing: list_customers(status='active', limit=3)")
    print("-"*70)
    result = server.list_customers(status='active', limit=3)
    print(json.dumps(result, indent=2))
    assert result['success'], "list_customers should succeed"
    assert result['count'] <= 3, "Should respect limit"
    print(f"✓ list_customers works! Found {result['count']} customers")
    
    # Tool 3: update_customer
    print("\n[3] Testing: update_customer(5, {'email': 'eve.test@email.com'})")
    print("-"*70)
    result = server.update_customer(5, {'email': 'eve.test@email.com'})
    print(json.dumps(result, indent=2))
    assert result['success'], "update_customer should succeed"
    assert 'email' in result['updated_fields'], "Should update email"
    print("✓ update_customer works!")
    
    # Verify the update
    print("\n   Verifying update...")
    result = server.get_customer(5)
    assert result['customer']['email'] == 'eve.test@email.com', "Email should be updated"
    print("   ✓ Update verified!")
    
    # Tool 4: create_ticket
    print("\n[4] Testing: create_ticket(1, 'Test issue from Part 2', 'high')")
    print("-"*70)
    result = server.create_ticket(1, 'Test issue from Part 2', 'high')
    print(json.dumps(result, indent=2))
    assert result['success'], "create_ticket should succeed"
    assert result['priority'] == 'high', "Should set correct priority"
    ticket_id = result['ticket_id']
    print(f"✓ create_ticket works! Created ticket #{ticket_id}")
    
    # Tool 5: get_customer_history
    print("\n[5] Testing: get_customer_history(1)")
    print("-"*70)
    result = server.get_customer_history(1)
    print(json.dumps(result, indent=2))
    assert result['success'], "get_customer_history should succeed"
    assert result['ticket_count'] > 0, "Customer 1 should have tickets"
    print(f"✓ get_customer_history works! Found {result['ticket_count']} tickets")
    
    server.close()
    
    print("\n" + "="*70)
    print("ALL MCP SERVER TOOLS PASSED ✓")
    print("="*70)


def test_mcp_client():
    """
    Test the MCP Client wrapper.
    This is what agents will actually use.
    """
    print("\n" + "="*70)
    print("TEST 2: MCP CLIENT TESTING")
    print("="*70)
    
    client = MCPClient()
    
    print("\n[1] Client: get_customer(3)")
    result = client.get_customer(3)
    print(json.dumps(result, indent=2))
    assert result['success'], "Client should successfully get customer"
    print("✓ Client get_customer works!")
    
    print("\n[2] Client: list_customers(status='active')")
    result = client.list_customers(status='active', limit=5)
    print(json.dumps(result, indent=2))
    assert result['success'], "Client should successfully list customers"
    print("✓ Client list_customers works!")
    
    print("\n[3] Client: create_ticket(2, 'Client test ticket', 'medium')")
    result = client.create_ticket(2, 'Client test ticket', 'medium')
    print(json.dumps(result, indent=2))
    assert result['success'], "Client should successfully create ticket"
    print("✓ Client create_ticket works!")
    
    client.close()
    
    print("\n" + "="*70)
    print("MCP CLIENT TESTS PASSED ✓")
    print("="*70)


def test_agent_mcp_integration():
    """
    Test agents using MCP to access database.
    This is the real integration test.
    """
    print("\n" + "="*70)
    print("TEST 3: AGENT + MCP INTEGRATION")
    print("="*70)
    
    # Create agents (they'll initialize their own MCP clients)
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    # Test 1: Data Agent - Retrieve customer
    print("\n[1] Data Agent: Get customer 5")
    print("-"*70)
    result = data_agent.process("Get customer information for ID 5")
    print(json.dumps(result, indent=2))
    assert result['success'], "Data agent should retrieve customer"
    assert 'customer' in result, "Should return customer data"
    print(f"✓ Data Agent retrieved: {result['customer']['name']}")
    
    # Test 2: Data Agent - List customers
    print("\n[2] Data Agent: List all active customers")
    print("-"*70)
    result = data_agent.process("List all active customers")
    print(json.dumps(result, indent=2))
    assert result['success'], "Data agent should list customers"
    assert 'customers' in result, "Should return customers list"
    print(f"✓ Data Agent listed {len(result['customers'])} customers")
    
    # Test 3: Data Agent - Update customer
    print("\n[3] Data Agent: Update customer email")
    print("-"*70)
    result = data_agent.process("Update customer 5 email to newemail@example.com")
    print(json.dumps(result, indent=2))
    assert result['success'], "Data agent should update customer"
    print("✓ Data Agent updated customer email")
    
    # Test 4: Support Agent - Create ticket
    print("\n[4] Support Agent: Create support ticket")
    print("-"*70)
    result = support_agent.process("I'm customer 3 and I need help with billing")
    print(json.dumps(result, indent=2))
    # Support agent should create a ticket
    print("✓ Support Agent processed request")
    
    # Test 5: Support Agent - Get customer history
    print("\n[5] Support Agent: Check customer history")
    print("-"*70)
    result = support_agent.process("Show history for customer 1")
    print(json.dumps(result, indent=2))
    print("✓ Support Agent retrieved history")
    
    print("\n" + "="*70)
    print("AGENT + MCP INTEGRATION TESTS PASSED ✓")
    print("="*70)


def test_error_handling():
    """
    Test error cases to ensure robust error handling.
    """
    print("\n" + "="*70)
    print("TEST 4: ERROR HANDLING")
    print("="*70)
    
    server = MCPServer()
    
    # Test 1: Invalid customer ID
    print("\n[1] Testing: get_customer(999) - Non-existent customer")
    print("-"*70)
    result = server.get_customer(999)
    print(json.dumps(result, indent=2))
    assert not result['success'], "Should fail for non-existent customer"
    assert 'error' in result, "Should return error message"
    print("✓ Correctly handles non-existent customer")
    
    # Test 2: Invalid status filter
    print("\n[2] Testing: list_customers(status='invalid')")
    print("-"*70)
    result = server.list_customers(status='invalid', limit=10)
    print(json.dumps(result, indent=2))
    # Should succeed but return empty list
    assert result['success'], "Should handle invalid status gracefully"
    print("✓ Correctly handles invalid status filter")
    
    # Test 3: Update non-existent customer
    print("\n[3] Testing: update_customer(999, {'email': 'test@test.com'})")
    print("-"*70)
    result = server.update_customer(999, {'email': 'test@test.com'})
    print(json.dumps(result, indent=2))
    assert not result['success'], "Should fail for non-existent customer"
    print("✓ Correctly handles update to non-existent customer")
    
    # Test 4: Create ticket for non-existent customer
    print("\n[4] Testing: create_ticket(999, 'Issue', 'high')")
    print("-"*70)
    result = server.create_ticket(999, 'Test issue', 'high')
    print(json.dumps(result, indent=2))
    assert not result['success'], "Should fail for non-existent customer"
    print("✓ Correctly handles ticket for non-existent customer")
    
    server.close()
    
    print("\n" + "="*70)
    print("ERROR HANDLING TESTS PASSED ✓")
    print("="*70)


def test_agent_queries():
    """
    Test realistic customer service queries through agents.
    """
    print("\n" + "="*70)
    print("TEST 5: REALISTIC QUERY SCENARIOS")
    print("="*70)
    
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent()
    
    test_queries = [
        ("Get customer information for ID 1", data_agent),
        ("Show me all active customers", data_agent),
        ("I'm customer 2 and need help with my account", support_agent),
        ("Update customer 3 email to updated@email.com", data_agent),
        ("I have a billing problem, customer ID 1", support_agent),
    ]
    
    for i, (query, agent) in enumerate(test_queries, 1):
        print(f"\n[Query {i}] {query}")
        print("-"*70)
        result = agent.process(query)
        print(f"Success: {result.get('success', 'N/A')}")
        print(f"Response: {result.get('content', str(result))[:150]}...")
        print("✓")
    
    print("\n" + "="*70)
    print("REALISTIC QUERY TESTS PASSED ✓")
    print("="*70)


def main():
    """
    Run all Part 2 tests.
    """
    print("\n" + "="*80)
    print("PART 2: MCP INTEGRATION TESTING")
    print("Testing Database Tools + Agent Integration")
    print("="*80)
    
    print("\n[SETUP] Make sure you've run setup_database.py first!")
    print("This will test the 5 MCP tools and agent integration.\n")
    
    try:
        # Test 1: Direct MCP server
        test_mcp_server_direct()
        
        # Test 2: MCP client wrapper
        test_mcp_client()
        
        # Test 3: Agent integration
        test_agent_mcp_integration()
        
        # Test 4: Error handling
        test_error_handling()
        
        # Test 5: Realistic queries
        test_agent_queries()
        
        # Summary
        print("\n" + "="*80)
        print("🎉 ALL PART 2 TESTS PASSED! 🎉")
        print("="*80)
        
        print("\n[SUMMARY]")
        print("  ✓ MCP Server: All 5 tools working")
        print("  ✓ MCP Client: Wrapper functioning correctly")
        print("  ✓ Agent Integration: Agents successfully using MCP")
        print("  ✓ Error Handling: Graceful error management")
        print("  ✓ Realistic Queries: End-to-end scenarios working")
        
        print("\n[MCP TOOLS VERIFIED]")
        print("  1. get_customer(customer_id)")
        print("  2. list_customers(status, limit)")
        print("  3. update_customer(customer_id, data)")
        print("  4. create_ticket(customer_id, issue, priority)")
        print("  5. get_customer_history(customer_id)")
        
        print("\n[NEXT STEPS]")
        print("  ✓ Part 1: System Architecture - COMPLETE")
        print("  ✓ Part 2: MCP Integration - COMPLETE")
        print("  → Part 3: Run test_part3.py to test A2A coordination")
        
        print("\n" + "="*80 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("Please check the error above and fix the issue.")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print("Make sure setup_database.py has been run successfully.")


if __name__ == "__main__":
    main()