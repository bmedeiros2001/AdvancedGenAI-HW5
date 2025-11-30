"""
True A2A Coordinator - NO SHARED STATE
Uses message passing only.
"""

from coordination.message_bus import MessageBus
from typing import Dict, Any
import time

class A2ACoordinator:
    """
    Coordinator for true Agent-to-Agent communication.
    """
    
    def __init__(self, router_agent, data_agent, support_agent, verbose=True):
        """Initialize coordinator with message bus"""
        self.verbose = verbose
        
        # Create message bus
        self.message_bus = MessageBus()
        
        # Set message bus for all agents
        router_agent.message_bus = self.message_bus
        data_agent.message_bus = self.message_bus
        support_agent.message_bus = self.message_bus
        
        # Register all agents
        self.message_bus.register_agent("Router Agent")
        self.message_bus.register_agent("Customer Data Agent")
        self.message_bus.register_agent("Support Agent")
        
        # Store agent references
        self.router = router_agent
        self.data_agent = data_agent
        self.support_agent = support_agent
        
        # Register specialists with router (by name only)
        self.router.specialist_agents["Customer Data Agent"] = "Customer Data Agent"
        self.router.specialist_agents["Support Agent"] = "Support Agent"
        
        if verbose:
            print("\n✅ A2A Coordinator initialized")
            print("   📨 Message Bus created")
            print("   📬 All agents registered\n")
    
    def _message_pump(self):
        """
        Background thread to process messages.
        Simulates agents running in parallel.
        """
        while self.running:
            agents_to_check = [
                ("Customer Data Agent", self.data_agent),
                ("Support Agent", self.support_agent)
            ]
            
            for agent_name, agent in agents_to_check:
                if self.message_bus.has_messages(agent_name):
                    msg = self.message_bus.receive_message(agent_name)
                    if msg:
                        if self.verbose:
                            print(f"   ⚙️ {agent_name} processing message...")
                        
                        # Agent processes message and sends reply
                        # (This happens in the background thread)
                        agent.process_message(msg)
            
            time.sleep(0.1)

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process query using TRUE A2A message passing.
        
        Flow:
        1. Start background message pump (to simulate other agents)
        2. Router analyzes query and sends messages
        3. Message pump picks up messages and triggers specialists
        4. Specialists respond
        5. Router receives response and finishes
        """
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"PROCESSING QUERY: {query}")
            print(f"{'='*70}\n")
        
        # Start message pump
        self.running = True
        import threading
        pump_thread = threading.Thread(target=self._message_pump)
        pump_thread.daemon = True
        pump_thread.start()
        
        try:
            # Router processes query (blocks waiting for response)
            result = self.router.process(query)
            
        finally:
            # Stop pump
            self.running = False
            pump_thread.join(timeout=1.0)
        
        # Get message history
        messages = self.message_bus.get_message_history()
        
        if self.verbose:
            print(f"\n{'='*70}")
            print("A2A MESSAGE HISTORY")
            print(f"{'='*70}")
            for msg in messages:
                print(f"  [{msg['from']} → {msg['to']}] {msg['content']}")
        
        return {
            "query": query,
            "final_response": result.get("content", str(result)),
            "messages": messages,
            "success": result.get("success", True)
        }