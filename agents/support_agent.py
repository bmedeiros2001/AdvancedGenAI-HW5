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
        
        Args:
            query: Support query
            context: Optional context (like customer data from Data Agent)
            
        Returns:
            Support response with recommendations
        """
        self.log_interaction("processing_support_query", {"query": query})
        
        # Assess priority
        priority = self.assess_priority(query)
        
        self.log_interaction("priority_assessed", {"priority": priority})
        
        # Determine if ticket creation is needed
        ticket_keywords = ["issue", "problem", "error", "bug", "not working"]
        needs_ticket = any(keyword in query.lower() for keyword in ticket_keywords)
        
        # Build response
        response = {
            "success": True,
            "priority": priority,
            "needs_ticket": needs_ticket
        }
        
        if needs_ticket:
            response["content"] = (
                f"[PLACEHOLDER] Would create a {priority}-priority ticket via MCP create_ticket(). "
                "MCP integration coming in Part 2."
            )
        else:
            response["content"] = (
                "I understand you need help. In Part 2, I'll be able to access "
                "customer history and provide specific solutions."
            )
        
        # If customer context is provided, acknowledge it
        if context and "customer_id" in context:
            response["content"] += f" Working with customer {context['customer_id']}."
        
        return response