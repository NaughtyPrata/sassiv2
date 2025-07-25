from typing import List, Dict, Any
import json
from .base_agent import BaseAgent, ChatMessage
from utils.prompt_loader import load_prompt

class SentimentAgent(BaseAgent):
    """Sentiment analysis agent with Sassi context"""
    
    def __init__(self):
        # Load mini personality for context and sentiment prompt
        self.personality_context = load_prompt("sassi_personality_mini.md")
        self.agent_prompt = load_prompt("sentiment_agent.md")
        
        # Combine mini personality with sentiment analysis instructions
        self.system_prompt = f"{self.personality_context}\n\n---\n\n{self.agent_prompt}"
        self.agent_type = "sentiment"
    
    async def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """Analyze sentiment of a single message with thinking process"""
        # Create a simple message list for analysis
        analysis_messages = [ChatMessage("user", message)]
        
        # Get raw response from Groq
        raw_response = await self._call_groq(analysis_messages, max_tokens=300, temperature=0.3)
        
        try:
            # Clean the response - remove markdown code blocks if present
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response.replace('```json', '').replace('```', '').strip()
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response.replace('```', '').strip()
            
            # Parse JSON response
            sentiment_data = json.loads(cleaned_response)
            
            # Add thinking tag if not present
            if "thinking" not in sentiment_data:
                sentiment_data["thinking"] = "Analysis completed without explicit reasoning"
            
            return sentiment_data
            
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            return {
                "emotion": "neutral",
                "intensity": 0.5,
                "confidence": 0.3,
                "secondary_emotions": [],
                "emotional_indicators": [],
                "thinking": f"JSON parsing failed: {str(e)}. Raw response: {raw_response[:100]}..."
            }
    
    async def generate_response(self, messages: List[ChatMessage]) -> str:
        """Not used for sentiment agent - use analyze_sentiment instead"""
        return "Sentiment agent should use analyze_sentiment method" 