"""
Router Agent - The Orchestrator
This agent receives queries and coordinates specialist agents.

analyze_intent: Uses keyword matching to figure out what the user wants
route_to_specialist: Sends queries to the right specialist agent
process: Main entry point that orchestrates everything
"""

from typing import Dict, Any, Optional, List
from agents import BaseAgent
from config.agent_config import ROUTER_AGENT_CONFIG

class RouterAgent(BaseAgent):
    """
    Router Agent coordinates between specialist agents.
    It's the entry point for all customer queries.
    """
    
    def __init__(self):
        """Initialize Router Agent with its configuration."""
        super().__init__(ROUTER_AGENT_CONFIG)
        
        # We'll store references to specialist agents here
        self.specialist_agents: Dict[str, BaseAgent] = {}
        
    def register_specialist(self, agent: BaseAgent):
        """
        Register a specialist agent that Router can delegate to.
        
        Args:
            agent: A specialist agent instance
        """
        self.specialist_agents[agent.name] = agent
        self.log_interaction("specialist_registered", {
            "specialist": agent.name,
            "capabilities": agent.capabilities
        })
    
    def analyze_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze the user's query to determine intent and required agents.
        
        Args:
            query: User's query string
            
        Returns:
            Dictionary with intent analysis:
            {
                "primary_intent": str,
                "requires_agents": List[str],
                "keywords": List[str],
                "complexity": str (simple/moderate/complex)
            }
        """
        query_lower = query.lower()
        
        # Intent detection based on keywords
        intents = []
        required_agents = []
        keywords = []
        
        # Check for customer data intent
        data_keywords = ["customer", "account", "information", "details", "id", "email", "phone"]
        if any(keyword in query_lower for keyword in data_keywords):
            intents.append("customer_data")
            required_agents.append("Customer Data Agent")
            keywords.extend([k for k in data_keywords if k in query_lower])
        
        # Check for support intent
        support_keywords = ["help", "issue", "problem", "support", "ticket", "cancel", "refund"]
        if any(keyword in query_lower for keyword in support_keywords):
            intents.append("customer_support")
            required_agents.append("Support Agent")
            keywords.extend([k for k in support_keywords if k in query_lower])
        
        # Check for update/modification intent
        update_keywords = ["update", "change", "modify", "upgrade"]
        if any(keyword in query_lower for keyword in update_keywords):
            if "customer_data" not in intents:
                intents.append("customer_data")
                required_agents.append("Customer Data Agent")
            keywords.extend([k for k in update_keywords if k in query_lower])
        
        # Determine complexity
        complexity = "simple"
        if len(required_agents) > 1:
            complexity = "complex"
        elif any(word in query_lower for word in ["all", "list", "every", "multiple"]):
            complexity = "moderate"
        
        intent_analysis = {
            "primary_intent": intents[0] if intents else "unknown",
            "all_intents": intents,
            "requires_agents": list(set(required_agents)),  # Remove duplicates
            "keywords": list(set(keywords)),
            "complexity": complexity,
            "original_query": query
        }
        
        self.log_interaction("intent_analyzed", intent_analysis)
        return intent_analysis
    
    def can_handle(self, query: str) -> bool:
        """
        Router can handle all queries - it's the entry point.
        
        Args:
            query: User query
            
        Returns:
            Always True for Router
        """
        return True
    
    def route_to_specialist(self, agent_name: str, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Route a query to a specific specialist agent.
        
        Args:
            agent_name: Name of the specialist agent
            query: Query to send to specialist
            context: Optional context information
            
        Returns:
            Response from specialist agent
        """
        if agent_name not in self.specialist_agents:
            return {
                "success": False,
                "error": f"Unknown specialist agent: {agent_name}"
            }
        
        specialist = self.specialist_agents[agent_name]
        
        self.log_interaction("routing_to_specialist", {
            "specialist": agent_name,
            "query": query,
            "context_provided": context is not None
        })
        
        # Call the specialist's process method
        response = specialist.process(query, context)
        
        self.log_interaction("received_from_specialist", {
            "specialist": agent_name,
            "response_preview": str(response)[:200]
        })
        
        return response
    
    def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a user query by analyzing intent and routing to specialists.
        
        Args:
            query: User's query
            context: Optional context (for multi-turn conversations)
            
        Returns:
            Final response to user
        """
        self.log_interaction("received_query", {"query": query})
        
        # Step 1: Analyze the intent
        intent_analysis = self.analyze_intent(query)
        
        # Step 2: Determine routing strategy
        required_agents = intent_analysis["requires_agents"]
        
        if not required_agents:
            # No clear intent - return clarification request
            return self.format_message(
                "I'm not sure I understand your request. Could you please provide more details?"
            )
        
        # Step 3: Route to appropriate agent(s)
        if len(required_agents) == 1:
            # Simple case: single agent
            response = self.route_to_specialist(required_agents[0], query, context)
            return self.format_message(response.get("content", str(response)))
        
        else:
            # Complex case: multiple agents needed (we'll expand this in Part 3)
            return self.format_message(
                f"This query requires coordination between: {', '.join(required_agents)}. "
                "(Multi-agent coordination will be implemented in Part 3)"
            )