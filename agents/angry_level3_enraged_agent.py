from .base_agent import BaseAgent, ChatMessage
from typing import List

class AngryLevel3EnragedAgent(BaseAgent):
    def __init__(self):
        super().__init__("angry-3-enraged.md")
    
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Generate enraged response based on conversation history"""
        return await self._call_groq(messages) 