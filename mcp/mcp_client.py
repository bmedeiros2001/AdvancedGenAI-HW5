from mcp.mcp_server import MCPServer
from typing import Dict, Any, Optional

class MCPClient:
    def __init__(self):
        """ initialize connection to MCP server """
        self.server = MCPServer()
        print(f"[MCP Client] Connected to MCP server")
    
    def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """ Get customer by ID """
        return self.server.get_customer(customer_id)
    
    def list_customers(self, status: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """List customers with optional status filter."""
        return self.server.list_customers(status, limit)
    
    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information."""
        return self.server.update_customer(customer_id, data)
    
    def create_ticket(self, customer_id: int, issue: str, priority: str = 'medium') -> Dict[str, Any]:
        """Create a support ticket."""
        return self.server.create_ticket(customer_id, issue, priority)
    
    def get_customer_history(self, customer_id: int) -> Dict[str, Any]:
        """Get customer's ticket history."""
        return self.server.get_customer_history(customer_id)
    
    def close(self):
        """Close MCP connection."""
        self.server.close()