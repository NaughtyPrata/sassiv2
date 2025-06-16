from typing import List
from .base_agent import BaseAgent, ChatMessage

class HappyLevel3EcstaticAgent(BaseAgent):
    """Happy Level 3: Ecstatic agent with overwhelming joy"""
    
    def __init__(self):
        super().__init__("happy-3-ecstatic.md")
    
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Generate ecstatic, joyful response"""
        return await self._call_groq(messages) 