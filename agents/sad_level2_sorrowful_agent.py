from typing import List
from .base_agent import BaseAgent, ChatMessage

class SadLevel2SorrowfulAgent(BaseAgent):
    """Sad Level 2: Sorrowful agent with deeper, more pronounced sadness"""
    
    def __init__(self):
        super().__init__("sad-2-sorrowful.md")
    
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Generate sorrowful response with deeper emotional weight"""
        return await self._call_groq(messages) 