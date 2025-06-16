from abc import ABC, abstractmethod
from typing import List
from openai import OpenAI
from fastapi import HTTPException
import os
from utils.prompt_loader import load_prompt

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatMessage:
    """Chat message model for agents"""
    def __init__(self, role: str, content: str, timestamp=None):
        self.role = role
        self.content = content
        self.timestamp = timestamp

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, prompt_file: str):
        self.system_prompt = load_prompt(prompt_file)
        self.agent_type = self.__class__.__name__.lower().replace('agent', '')
    
    @abstractmethod
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Generate response based on conversation history"""
        pass
    
    async def _call_openai(self, messages: List[ChatMessage], max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Common OpenAI API call logic"""
        try:
            # Convert messages to OpenAI format
            openai_messages = [{"role": "system", "content": self.system_prompt}]
            for msg in messages:
                openai_messages.append({"role": msg.role, "content": msg.content})
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}") 