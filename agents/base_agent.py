from abc import ABC, abstractmethod
from typing import List
from groq import Groq
from fastapi import HTTPException
import os
from utils.prompt_loader import load_prompt

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ChatMessage:
    """Chat message model for agents"""
    def __init__(self, role: str, content: str, timestamp=None):
        self.role = role
        self.content = content
        self.timestamp = timestamp

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, prompt_file: str):
        # Load core personality and agent-specific prompt
        self.personality_prompt = load_prompt("sassi_personality.md")
        self.agent_prompt = load_prompt(prompt_file)
        
        # Combine personality with agent-specific behavior
        self.system_prompt = f"{self.personality_prompt}\n\n---\n\n{self.agent_prompt}"
        self.agent_type = self.__class__.__name__.lower().replace('agent', '')
    
    @abstractmethod
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Generate response based on conversation history"""
        pass
    
    def _trim_conversation_history(self, messages: List[ChatMessage], max_messages: int = 20) -> List[ChatMessage]:
        """Trim conversation history to maintain context window while preserving memory"""
        if len(messages) <= max_messages:
            return messages
        
        # Keep the most recent messages for better context
        return messages[-max_messages:]
    
    async def _call_groq(self, messages: List[ChatMessage], max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """Common Groq API call logic with expanded context window"""
        try:
            # Trim conversation history to manage context window
            trimmed_messages = self._trim_conversation_history(messages)
            
            # Convert messages to Groq format
            groq_messages = [{"role": "system", "content": self.system_prompt}]
            for msg in trimmed_messages:
                groq_messages.append({"role": msg.role, "content": msg.content})
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=groq_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False  # For now, let's use non-streaming for simplicity
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}") 