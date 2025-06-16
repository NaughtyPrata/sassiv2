from typing import List
from .base_agent import BaseAgent, ChatMessage

class HappyLevel1PleasedAgent(BaseAgent):
    """Happy Level 1: Pleased agent with gentle positivity"""
    
    def __init__(self):
        super().__init__("happy-1-pleased.md")
    
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Generate gently positive response"""
        return await self._call_groq(messages) 