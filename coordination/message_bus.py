"""
Message Bus - True A2A Communication
This enables agents to send/receive messages WITHOUT shared state.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import queue
import json

@dataclass
class Message:
    """A message between agents"""
    id: str
    from_agent: str
    to_agent: str
    content: str
    data: Optional[Dict] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "from": self.from_agent,
            "to": self.to_agent,
            "content": self.content,
            "data": self.data,
            "timestamp": self.timestamp
        }


class MessageBus:
    """
    Message Bus for Agent-to-Agent communication.
    
    Each agent has its own inbox (queue).
    Agents send messages to other agents' inboxes.
    No shared state - only message passing.
    """
    
    def __init__(self):
        # Each agent has its own inbox
        self.inboxes: Dict[str, queue.Queue] = {}
        
        # Message history for debugging
        self.message_history: List[Message] = []
        
        # Message ID counter
        self.message_counter = 0
    
    def register_agent(self, agent_name: str):
        """Register an agent and create its inbox"""
        if agent_name not in self.inboxes:
            self.inboxes[agent_name] = queue.Queue()
            print(f"📬 Registered agent inbox: {agent_name}")
    
    def send_message(self, from_agent: str, to_agent: str, content: str, data: Optional[Dict] = None):
        """
        Send a message from one agent to another.
        This is TRUE message passing - no shared state!
        """
        
        if to_agent not in self.inboxes:
            raise ValueError(f"Agent {to_agent} not registered")
        
        # Create message
        self.message_counter += 1
        message = Message(
            id=f"msg_{self.message_counter}",
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            data=data
        )
        
        # Put message in recipient's inbox
        self.inboxes[to_agent].put(message)
        
        # Log for debugging
        self.message_history.append(message)
        
        print(f"📨 [{from_agent} → {to_agent}] {content[:60]}...")
        
        return message.id
    
    def receive_message(self, agent_name: str, timeout: float = 1.0) -> Optional[Message]:
        """
        Agent receives a message from its inbox.
        Returns None if no message available.
        """
        
        if agent_name not in self.inboxes:
            raise ValueError(f"Agent {agent_name} not registered")
        
        try:
            message = self.inboxes[agent_name].get(timeout=timeout)
            print(f"📬 [{agent_name}] Received message from {message.from_agent}")
            return message
        except queue.Empty:
            return None
    
    def has_messages(self, agent_name: str) -> bool:
        """Check if agent has pending messages"""
        return not self.inboxes[agent_name].empty()
    
    def get_message_history(self) -> List[Dict]:
        """Get all messages sent (for debugging)"""
        return [msg.to_dict() for msg in self.message_history]


class AgentMemory:
    """
    Private memory for each agent - NO sharing!
    Each agent instance has its own AgentMemory.
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.data: Dict[str, Any] = {}
        self.conversation_history: List[Dict] = []
    
    def store(self, key: str, value: Any):
        """Store data in private memory"""
        self.data[key] = value
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from private memory"""
        return self.data.get(key)
    
    def add_to_history(self, entry: Dict):
        """Add to conversation history"""
        self.conversation_history.append(entry)
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history