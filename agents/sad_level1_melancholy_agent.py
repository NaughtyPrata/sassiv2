from typing import List
from .base_agent import BaseAgent, ChatMessage

class SadLevel1MelancholyAgent(BaseAgent):
    """Sad Level 1: Melancholy agent with gentle, wistful sadness"""
    
    def __init__(self):
        super().__init__("sad-1-melancholy.md")
    
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Generate gently melancholy response"""
        return await self._call_groq(messages) 