"""
Support Agent - Customer Service Specialist
Handles support queries and ticket management.
"""

from typing import Dict, Any, Optional
from agents import BaseAgent
from config.agent_config import SUPPORT_AGENT_CONFIG


class SupportAgent(BaseAgent):
    """
    Specialist agent for customer support operations.
    """
    
    def __init__(self):
        """Initialize Support Agent."""
        super().__init__(SUPPORT_AGENT_CONFIG)
        
        # Placeholder for MCP client (will implement in Part 2)
        self.mcp_client = None
    
    def can_handle(self, query: str) -> bool:
        """
        Check if this agent can handle the query.
        
        Args:
            query: User query
            
        Returns:
            True if query relates to support/help
        """
        support_keywords = ["help", "issue", "problem", "support", "ticket", 
                          "cancel", "refund", "billing", "error"]
        return any(keyword in query.lower() for keyword in support_keywords)
    
    def assess_priority(self, query: str) -> str:
        """
        Assess the priority level of a support issue.
        
        Args:
            query: User's query describing their issue
            
        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        query_lower = query.lower()
        
        # High priority indicators
        high_priority_keywords = ["urgent", "immediately", "asap", "critical", 
                                 "billing", "charged", "refund", "security", 
                                 "hack", "breach", "down", "outage"]
        if any(keyword in query_lower for keyword in high_priority_keywords):
            return "high"
        
        # Medium priority indicators  
        medium_priority_keywords = ["upgrade", "change", "modify", "request", 
                                   "feature", "improvement"]
        if any(keyword in query_lower for keyword in medium_priority_keywords):
            return "medium"
        
        # Default to low priority
        return "low"
    
    def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process support requests.
        """
        self.log_interaction("processing_support_query", {"query": query})

        # initialize MCP client
        if not self.mcp_client:
            from mcp.mcp_client import MCPClient
            self.mcp_client = MCPClient()
        
        # Assess priority
        priority = self.assess_priority(query)
        self.log_interaction("priority_assessed", {"priority": priority})

        # extract customer ID if present
        import re
        customer_id = None
        id_patterns = [r'id\s+(\d+)', r'customer\s+(\d+)', r'#(\d+)']
        for pattern in id_patterns:
            match = re.search(pattern, query.lower())
            if match:
                customer_id = int(match.group(1))
                break
        
        # Determine if ticket creation is needed
        ticket_keywords = ["issue", "problem", "error", "bug", "not working", "help", "charged"]
        needs_ticket = any(keyword in query.lower() for keyword in ticket_keywords)
        
        # Build response
        response = {
            "success": True,
            "priority": priority,
            "needs_ticket": needs_ticket
        }
        
        if needs_ticket and customer_id:

            result = self.mcp_client.create_ticket(
                customer_id=customer_id,
                issue=query,
                priority=priority
            )

            if result['success']:
                response["content"] = (
                    f"I've created a {priority}-priority ticket (#{result['ticket_id']}) for customer {customer_id}. Our team will assist you shortly"
                )
                response["ticket_id"] = result['ticket_id']
            else:
                response["content"] = f"Error creating ticket: {result['error']}"
                response["success"] = False

        elif needs_ticket and not customer_id:
            response["content"] = (
                "I understand you need help. Could you provide your customer ID so I can create a support ticket for you?"
            )

        else:
            # get customer history if we have ID
            if customer_id:
                history = self.mcp_client.get_customer_history(customer_id)
                if history['success']:
                    ticket_count = history['ticket_count']
                    response["content"] = (
                        f"Hello customer {customer_id}, I understand you need help. I see you have {ticket_count} previous ticket(s). How can I assist you today?"
                    )
                else: 
                    response["content"] = "I understand you need help. How can I assist you?"
            else:
                response["content"] = "I understand you need help. How can I assist you?"

        # If customer context is provided from another agent, acknowledge it
        if context and "customer_id" in context:
            customer = context["customer"]
            response["content"] = f"Hello {customer['name']}, " + response["content"]
        
        return response