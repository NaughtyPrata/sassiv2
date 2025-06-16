from typing import List
from .base_agent import BaseAgent, ChatMessage

class CheerfulAgent(BaseAgent):
    """Cheerful agent with upbeat enthusiasm"""
    
    def __init__(self):
        super().__init__("happy-2-cheerful.md")
    
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Generate cheerful, enthusiastic response"""
        return await self._call_groq(messages) 