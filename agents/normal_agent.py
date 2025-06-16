from typing import List
from .base_agent import BaseAgent, ChatMessage

class NormalAgent(BaseAgent):
    """Normal agent with balanced, professional responses"""
    
    def __init__(self):
        super().__init__("normal_agent.md")
    
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Generate balanced, professional response"""
        return await self._call_groq(messages) 