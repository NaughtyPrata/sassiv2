from typing import List
from .base_agent import BaseAgent, ChatMessage

class SadLevel3DepressedAgent(BaseAgent):
    """Sad Level 3: Depressed agent with profound, overwhelming sadness"""
    
    def __init__(self):
        super().__init__("sad-3-depressed.md")
    
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Generate depressed response with profound emotional struggle"""
        return await self._call_groq(messages) 