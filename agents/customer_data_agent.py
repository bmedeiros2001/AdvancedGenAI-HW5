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
    
    def __init__(self):
        """Initialize Customer Data Agent."""
        super().__init__(CUSTOMER_DATA_AGENT_CONFIG)
        
        # Placeholder for MCP client (will implement in Part 2)
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
        
        Args:
            query: Query about customer data
            context: Optional context from Router
            
        Returns:
            Response with customer data or status
        """
        self.log_interaction("processing_query", {"query": query})
        
        query_lower = query.lower()
        
        # Determine the operation type
        if "get" in query_lower or "show" in query_lower or "find" in query_lower:
            operation = "retrieve"
        elif "update" in query_lower or "change" in query_lower or "modify" in query_lower:
            operation = "update"
        elif "list" in query_lower or "all" in query_lower:
            operation = "list"
        else:
            operation = "retrieve"  # Default
        
        # For now, return a placeholder response
        # In Part 2, we'll actually call MCP tools here
        if operation == "retrieve":
            customer_id = self.extract_customer_id(query)
            if customer_id:
                return {
                    "success": True,
                    "operation": "retrieve",
                    "content": f"[PLACEHOLDER] Would fetch customer {customer_id} via MCP get_customer()",
                    "note": "MCP integration coming in Part 2"
                }
            else:
                return {
                    "success": False,
                    "content": "Please provide a customer ID"
                }
        
        elif operation == "list":
            return {
                "success": True,
                "operation": "list",
                "content": "[PLACEHOLDER] Would list customers via MCP list_customers()",
                "note": "MCP integration coming in Part 2"
            }
        
        elif operation == "update":
            return {
                "success": True,
                "operation": "update",
                "content": "[PLACEHOLDER] Would update customer via MCP update_customer()",
                "note": "MCP integration coming in Part 2"
            }
        
        return {
            "success": False,
            "content": "Could not determine operation type"
        }