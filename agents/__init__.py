from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class BaseAgent:
    """
    Base class for agents with PRIVATE memory (no shared state).
    Agents communicate via message passing only.
    """

    def __init__(self, config: Dict[str, Any], message_bus=None):
        """
        Initialize the agent with its configuration.
        
        Args:
            config: Dictionary containing agent configuration
            message_bus: MessageBus instance for A2A communication
        """
        self.name = config["name"]
        self.role = config["role"]
        self.description = config["description"]
        self.system_instruction = config["system_instruction"]
        self.capabilities = config.get("capabilities", [])
        self.mcp_tools = config.get("mcp_tools", [])
        
        # Message bus for A2A communication
        self.message_bus = message_bus
        
        # PRIVATE memory - not shared with other agents!
        self.private_memory: Dict[str, Any] = {}
        
        # Interaction history for debugging
        self.interaction_history: List[Dict] = []
        
    def log_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """Log an interaction for debugging"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "type": interaction_type,
            "data": data
        }
        self.interaction_history.append(log_entry)
        
        # Print for visibility
        json_str = json.dumps(data, indent=2)
        indented_json = '\n'.join('    ' + line for line in json_str.split('\n'))
        print(f"    [{self.name}] {interaction_type}:\n{indented_json}")
    
    def send_message(self, to_agent: str, content: str, data: Optional[Dict] = None):
        """Send message to another agent via message bus"""
        if self.message_bus:
            return self.message_bus.send_message(self.name, to_agent, content, data)
        else:
            print(f"Warning: No message bus available for {self.name}")
    
    def receive_message(self, timeout: float = 1.0):
        """Receive message from message bus"""
        if self.message_bus:
            return self.message_bus.receive_message(self.name, timeout)
        return None
    
    def store_in_memory(self, key: str, value: Any):
        """Store data in PRIVATE memory (not accessible to other agents)"""
        self.private_memory[key] = value
    
    def retrieve_from_memory(self, key: str) -> Optional[Any]:
        """Retrieve data from private memory"""
        return self.private_memory.get(key)
    
    def can_handle(self, query: str) -> bool:
        """Determine if this agent can handle a given query"""
        raise NotImplementedError("Subclasses must implement can_handle()")
    
    def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a query and return a response"""
        raise NotImplementedError("Subclasses must implement process()")
    
    def get_capabilities_summary(self) -> str:
        """Return a summary of what this agent can do"""
        return f"{self.name} can: {', '.join(self.capabilities)}"