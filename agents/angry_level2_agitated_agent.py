from .base_agent import BaseAgent, ChatMessage
from typing import List

class AngryLevel2AgitatedAgent(BaseAgent):
    def __init__(self):
        super().__init__("angry-2-agitated.md")
    
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Generate agitated response based on conversation history"""
        return await self._call_groq(messages) 