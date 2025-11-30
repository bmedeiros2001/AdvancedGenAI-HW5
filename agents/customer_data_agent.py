"""
Customer Data Agent - Database Specialist
Handles all customer data operations (will connect to MCP in Part 2).
"""

from typing import Dict, Any, Optional
from agents import BaseAgent
from config.agent_config import CUSTOMER_DATA_AGENT_CONFIG


class CustomerDataAgent(BaseAgent):
    """
    Specialist agent for customer data operations.
    In Part 2, this will connect to MCP server.
    """
    
    def __init__(self, message_bus=None):
        """Initialize Customer Data Agent with message bus"""
        super().__init__(CUSTOMER_DATA_AGENT_CONFIG, message_bus)
        
        # Register with message bus
        if self.message_bus:
            self.message_bus.register_agent(self.name)
        
        # MCP client
        self.mcp_client = None
    
    def can_handle(self, query: str) -> bool:
        """
        Check if this agent can handle the query.
        
        Args:
            query: User query
            
        Returns:
            True if query relates to customer data
        """
        data_keywords = ["customer", "account", "information", "details", "id", 
                        "email", "phone", "update", "get", "list"]
        return any(keyword in query.lower() for keyword in data_keywords)
    
    def process_message(self, message):
        """
        Process incoming message from another agent.
        This is the TRUE A2A entry point!
        """
        query = message.data.get("query")
        context = message.data.get("context", {})
        
        # Process the query
        result = self.process(query, context)
        
        # Send response back to sender
        self.send_message(
            to_agent=message.from_agent,
            content="Query processed",
            data=result
        )
        
        return result
    
    def extract_customer_id(self, query: str) -> Optional[str]:
        """
        Extract customer ID from query using simple pattern matching.
        
        Args:
            query: User query
            
        Returns:
            Customer ID if found, None otherwise
        """
        import re
        
        # Look for patterns like "ID 12345" or "customer 12345"
        patterns = [
            r'id\s+(\d+)',
            r'customer\s+(\d+)',
            r'#(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return match.group(1)
        
        return None
    
    def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process customer data requests.
        """
        self.log_interaction("processing_query", {"query": query})
        
        query_lower = query.lower()

        # initialize MCP client
        if not self.mcp_client:
            from mcp.mcp_client import MCPClient
            self.mcp_client = MCPClient()
        
        # Determine the operation type
        if "get" in query_lower or "show" in query_lower or "find" in query_lower:
            operation = "retrieve"
        elif "update" in query_lower or "change" in query_lower or "modify" in query_lower:
            operation = "update"
        elif "list" in query_lower or "all" in query_lower:
            operation = "list"
        else:
            operation = "retrieve"  # Default
        
        # RETRIEVE operation
        if operation == "retrieve":
            customer_id = self.extract_customer_id(query)
            if customer_id:

                result = self.mcp_client.get_customer(int(customer_id))

                if result['success']:
                    customer = result['customer']
                    return {
                        "success": True,
                        "operation": "retrieve",
                        "customer": customer,
                        "content": f"Customer {customer['id']}: {customer['name']} ({customer['status']})"
                    }
                else:
                    return {
                        "success": False,
                        "operation": "retrieve",
                        "content": f"Failed to retrieve customer: {result.get('error', 'Unknown error')}"
                    }
                
            else:
                return {
                    "success": False,
                    "content": "Please provide a customer ID"
                }
        
        # LIST operation
        elif operation == "list":

            # extract status if mentioned
            status = 'active' if 'active' in query_lower else None

            # mcp call
            result = self.mcp_client.list_customers(status=status, limit=10)

            if result['success']:
                customers = result['customers']
                customer_list = "\n".join([
                    f"  - Customer {c['id']}: {c['name']} ({c['status']})"
                    for c in customers
                ])
                return {
                    "success": True,
                    "operation": "list",
                    "customers": customers,
                    "content": f"Found {result['count']} customers:\n{customer_list}"
                }
            else:
                return {
                    "success": False,
                    "operation": "list",
                    "content": f"Failed to list customers: {result.get('error', 'Unknown error')}"
                }
            
        # UPDATE operation
        elif operation == "update":
            customer_id = self.extract_customer_id(query)
            if not customer_id:
                return {
                    "success": False,
                    "content": "Please provide a customer ID to update"
                }
            
            # Extract update data from query (simple email extraction for now)
            import re
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', query)
            
            if email_match:
                new_email = email_match.group(0)
                # ACTUAL MCP CALL
                result = self.mcp_client.update_customer(int(customer_id), {'email': new_email})
                
                if result['success']:
                    return {
                        "success": True,
                        "operation": "update",
                        "content": f"Updated customer {customer_id}: {result['updated_fields']}"
                    }
                else:
                    return {
                        "success": False,
                        "content": result['error']
                    }
            else:
                return {
                    "success": False,
                    "content": "Could not find data to update in query"
                }
        
        return {
            "success": False,
            "content": "Could not determine operation type"
        }