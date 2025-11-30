from typing import Dict, Any, Optional, List
from agents import BaseAgent
from config.agent_config import ROUTER_AGENT_CONFIG
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class RouterAgent(BaseAgent):
    """
    Router Agent coordinates between specialist agents.
    It's the entry point for all customer queries.
    """
    
    def __init__(self, message_bus=None):
        """Initialize Router Agent with message bus"""
        super().__init__(ROUTER_AGENT_CONFIG, message_bus)
        
        # Register with message bus
        if self.message_bus:
            self.message_bus.register_agent(self.name)
        
        # Store references to specialist agents
        self.specialist_agents: Dict[str, str] = {}  # Now stores agent names, not objects
        

    def route_to_specialist(self, agent_name: str, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Route a query to a specialist by SENDING A MESSAGE (true A2A).
        No direct function calls - only message passing!
        """
        
        if agent_name not in self.specialist_agents:
            return {
                "success": False,
                "error": f"Unknown specialist agent: {agent_name}"
            }
        
        # Send message to specialist
        self.send_message(
            to_agent=agent_name,
            content=f"Please process: {query}",
            data={"query": query, "context": context or {}}
        )
        
        self.log_interaction("sent_message_to_specialist", {
            "specialist": agent_name,
            "query": query
        })
        
        # Wait for response message
        response_message = self.receive_message(timeout=5.0)
        
        if response_message:
            self.log_interaction("received_from_specialist", {
                "specialist": response_message.from_agent,
                "response_preview": str(response_message.data)[:200]
            })
            
            return response_message.data
        else:
            return {
                "success": False,
                "error": "No response from specialist"
            }
    
    
    def analyze_intent(self, query: str) -> Dict[str, Any]:
        """
        Use OpenAI GPT to analyze user's query intent.
        """
        
        prompt = f"""Analyze this customer service query and respond with JSON:

    Query: "{query}"

    Determine:
    1. What agents are needed? (Customer Data Agent, Support Agent, or both)
    2. What's the complexity? (simple, moderate, complex)
    3. What's the primary intent?

    Respond ONLY with valid JSON in this format:
    {{
        "primary_intent": "customer_data" | "customer_support" | "both",
        "requires_agents": ["Customer Data Agent"] or ["Support Agent"] or ["Customer Data Agent", "Support Agent"],
        "complexity": "simple" | "moderate" | "complex",
        "reasoning": "brief explanation"
    }}

    Examples:
    - "Get customer 5" → {{"primary_intent": "customer_data", "requires_agents": ["Customer Data Agent"], "complexity": "simple"}}
    - "I need help, customer ID 5" → {{"primary_intent": "both", "requires_agents": ["Customer Data Agent", "Support Agent"], "complexity": "moderate"}}
    """
        
        try:
            # Call OpenAI GPT
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Cheap and fast
                messages=[
                    {"role": "system", "content": "You are a query analyzer. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0  # Deterministic
            )
            
            # Parse JSON response
            import json
            
            # Handle potential None for message content
            message_content = response.choices[0].message.content
            if message_content is None:
                raise ValueError("Received None content from OpenAI API")

            intent_analysis = json.loads(message_content.strip())
            
            # Add original query
            intent_analysis["original_query"] = query
            intent_analysis["llm_used"] = "gpt-3.5-turbo"
            
            self.log_interaction("gpt_intent_analyzed", intent_analysis)
            return intent_analysis
            
        except Exception as e:
            # Fallback to keyword matching if GPT fails
            self.log_interaction("gpt_error", {"error": str(e), "using_fallback": True})
            return self._fallback_keyword_analysis(query)

    def _fallback_keyword_analysis(self, query: str) -> Dict[str, Any]:
        """Fallback to your original keyword matching if Gemini fails"""
        query_lower = query.lower()
        
        intents = []
        required_agents = []
        keywords = []
        
        # Your original keyword logic here...
        data_keywords = ["customer", "account", "information", "details", "id", "email", "phone"]
        if any(keyword in query_lower for keyword in data_keywords):
            intents.append("customer_data")
            required_agents.append("Customer Data Agent")
        
        support_keywords = ["help", "issue", "problem", "support", "ticket", "cancel", "refund"]
        if any(keyword in query_lower for keyword in support_keywords):
            intents.append("customer_support")
            required_agents.append("Support Agent")
        
        complexity = "simple"
        if len(required_agents) > 1:
            complexity = "complex"
        
        return {
            "primary_intent": intents[0] if intents else "unknown",
            "requires_agents": list(set(required_agents)),
            "complexity": complexity,
            "original_query": query,
            "method": "fallback_keywords"
        }
    
    def can_handle(self, query: str) -> bool:
        """
        Router can handle all queries - it's the entry point.
        
        Args:
            query: User query
            
        Returns:
            Always True for Router
        """
        return True
    
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
            return {
                "success": False,
                "content": "I'm not sure I understand your request. Could you please provide more details?"
            }
        
        # Step 3: Route based on intent
        primary_intent = intent_analysis.get("primary_intent")
        complexity = intent_analysis.get("complexity")
        
        # SCENARIO 1: TASK ALLOCATION (Simple or Moderate)
        # "Get customer info" OR "Help with account" (might need data first)
        if complexity == "simple" or (primary_intent == "customer_support" and complexity == "moderate"):
            return self._handle_task_allocation(query, intent_analysis)
            
        # SCENARIO 2: NEGOTIATION (Complex - Multiple Intents)
        # "Cancel subscription + billing issues"
        elif complexity == "complex" and len(required_agents) > 1:
            return self._handle_negotiation(query, intent_analysis)
            
        # SCENARIO 3: MULTI-STEP (Complex - Batch/Aggregated)
        # "Status of ALL high-priority tickets..."
        elif "all" in query.lower() or "list" in query.lower():
             return self._handle_multi_step(query, intent_analysis)
             
        # Default fallback
        return self._handle_task_allocation(query, intent_analysis)

    def _handle_task_allocation(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle simple task allocation.
        If support is needed, check if we need customer data first.
        """
        required_agents = intent.get("requires_agents", [])
        
        # If it's just data, route to data agent
        if "Customer Data Agent" in required_agents and "Support Agent" not in required_agents:
            return self.route_to_specialist("Customer Data Agent", query)
            
        # If it's support, we might need customer data first
        if "Support Agent" in required_agents:
            # Check if query implies we need to know WHO the customer is
            # (Simple heuristic: if it mentions "my account" or "customer ID", fetch data first)
            needs_data = "id" in query.lower() or "customer" in query.lower()
            
            context = {}
            if needs_data:
                # Step 1: Get Data
                self.log_interaction("coordination_step", "Fetching customer data for support context")
                data_response = self.route_to_specialist("Customer Data Agent", query)
                
                if data_response.get("success"):
                    context["customer"] = data_response.get("customer")
                    context["customer_id"] = data_response.get("customer", {}).get("id")
            
            # Step 2: Route to Support with context
            return self.route_to_specialist("Support Agent", query, context)
            
        return {"success": False, "error": "Could not determine allocation"}

    def _handle_negotiation(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle negotiation between agents.
        Router mediates: Support -> asks for info -> Router -> Data -> Router -> Support
        """
        self.log_interaction("coordination_start", "Starting Negotiation Flow")
        
        # Step 1: Ask Support Agent if they can handle it
        support_response = self.route_to_specialist("Support Agent", query)
        
        # Step 2: Check if Support Agent requested more info (Negotiation)
        if support_response.get("needs_context"):
            missing_info = support_response.get("missing_info") # e.g., "billing_history"
            self.log_interaction("negotiation_step", f"Support requested: {missing_info}")
            
            # Step 3: Ask Data Agent for the missing info
            # We construct a specific query for the data agent
            data_query = f"Get {missing_info} for customer {support_response.get('customer_id')}"
            data_response = self.route_to_specialist("Customer Data Agent", data_query)
            
            # Step 4: Provide info back to Support Agent
            context = {
                "negotiated_data": data_response, 
                "customer_id": support_response.get("customer_id")
            }
            final_response = self.route_to_specialist("Support Agent", query, context)
            return final_response
            
        return support_response

    def _handle_multi_step(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle multi-step coordination (e.g., List -> Process Each).
        """
        self.log_interaction("coordination_start", "Starting Multi-Step Flow")
        
        # Step 1: Decompose - Get the list of customers first
        # (Assuming query is like "Status of tickets for all active customers")
        list_query = "List all active customers" # Simplified decomposition
        
        data_response = self.route_to_specialist("Customer Data Agent", list_query)
        
        if not data_response.get("success"):
            return data_response
            
        customers = data_response.get("customers", [])
        results = []
        
        # Step 2: Iterate and process for each customer
        # (Limit to 3 for demo purposes to avoid timeout)
        for customer in customers[:3]:
            cid = customer['id']
            cname = customer['name']
            
            # Step 3: Ask Support Agent for tickets for this customer
            ticket_query = f"Get ticket status for customer {cid}"
            support_response = self.route_to_specialist("Support Agent", ticket_query)
            
            results.append({
                "customer": cname,
                "status": support_response.get("content")
            })
            
        # Step 4: Synthesize final answer
        summary = "\n".join([f"- {r['customer']}: {r['status']}" for r in results])
        return {
            "success": True,
            "content": f"Here is the status report:\n{summary}",
            "details": results
        }