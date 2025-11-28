from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class BaseAgent:
    """
    Base class for all agents in the system. Provides common functionality like:
    - Storing agent configuration
    - Logging interactions
    - Formatting messages
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the agent with its configuration.
        
        Args:
            config: Dictionary containing agent configuration (name, role, system_instruction, capabilities, etc.)
        """
        self.name = config["name"]
        self.role = config["role"]
        self.description = config["description"]
        self.system_instruction = config["system_instruction"]
        self.capabilities = config.get("capabilities", [])
        self.mcp_tools = config.get("mcp_tools", [])
        
        # Interaction history for debugging and logging
        self.interaction_history: List[Dict] = []
        
    def log_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """
        Log an interaction for debugging and transparency.
        
        Args:
            interaction_type: Type of interaction (e.g., "received_query", "called_tool")
            data: Data associated with the interaction
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "type": interaction_type,
            "data": data
        }
        self.interaction_history.append(log_entry)
        
        # Print for visibility during development
        print(f"[{self.name}] {interaction_type}: {json.dumps(data, indent=2)}")
    
    def format_message(self, content: str, recipient: Optional[str] = None) -> Dict[str, Any]:
        """
        Format a message to send to another agent or return to user.
        
        Args:
            content: The message content
            recipient: Who this message is for (optional)
            
        Returns:
            Formatted message dictionary
        """
        return {
            "from": self.name,
            "to": recipient or "user",
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
    
    def can_handle(self, query: str) -> bool:
        """
        Determine if this agent can handle a given query.
        Subclasses should override this method.
        
        Args:
            query: The user query
            
        Returns:
            Boolean indicating if agent can handle the query
        """
        raise NotImplementedError("Subclasses must implement can_handle()")
    
    def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a query and return a response.
        Subclasses should override this method.
        
        Args:
            query: The user query to process
            context: Optional context from other agents
            
        Returns:
            Response dictionary
        """
        raise NotImplementedError("Subclasses must implement process()")
    
    def get_capabilities_summary(self) -> str:
        """
        Return a summary of what this agent can do.
        Useful for other agents to understand capabilities.
        
        Returns:
            String description of capabilities
        """
        return f"{self.name} can: {', '.join(self.capabilities)}"