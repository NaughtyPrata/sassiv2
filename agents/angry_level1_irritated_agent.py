from .base_agent import BaseAgent, ChatMessage
from typing import List

class AngryLevel1IrritatedAgent(BaseAgent):
    def __init__(self):
        super().__init__("angry-1-irritated.md", skip_personality=True)
    
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Generate irritated response based on conversation history"""
        return await self._call_groq(messages) 