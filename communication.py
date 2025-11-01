from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

class AgentMessage(BaseModel):
    """Standard message format for agent communication"""
    sender: str
    receiver: str
    content: Any
    message_type: str  # "research_data", "analysis", "error", "retry"
    timestamp: str
    metadata: Dict[str, Any] = {}

class MessageQueue:
    """Simple in-memory message queue for agent communication"""
    def __init__(self):
        self.messages = []
        self.logger = logging.getLogger(__name__)
    
    def send_message(self, message: AgentMessage):
        """Send message between agents"""
        self.messages.append(message)
        self.logger.info(f"{message.sender} -> {message.receiver}: {message.message_type}")
    
    def receive_message(self, agent_name: str) -> Optional[AgentMessage]:
        """Receive message for specific agent"""
        for i, msg in enumerate(self.messages):
            if msg.receiver == agent_name:
                return self.messages.pop(i)
        return None