from typing import List, Dict, Any, Tuple
from agents.normal_agent import NormalAgent
from agents.sentiment_agent import SentimentAgent
from agents.base_agent import ChatMessage

class Orchestrator:
    """Enhanced orchestrator that manages conversation flow with sentiment analysis"""
    
    def __init__(self):
        self.normal_agent = NormalAgent()
        self.sentiment_agent = SentimentAgent()
        self.current_agent = "normal"
        self.conversation_state = {}
    
    async def process_message(self, message: str, conversation_history: List[ChatMessage]) -> Tuple[str, str, Dict[str, Any]]:
        """
        Process user message and return response with agent type and sentiment analysis
        
        Returns:
            Tuple of (response, agent_type, analysis_data)
        """
        
        # Step 1: Analyze sentiment
        sentiment_analysis = await self.sentiment_agent.analyze_sentiment(message)
        
        # Step 2: Make routing decision (for now, always use normal agent)
        orchestrator_thinking = {
            "current_agent": self.current_agent,
            "next_agent": "normal",
            "action": "maintain",
            "thinking": f"Detected {sentiment_analysis.get('emotion', 'unknown')} with intensity {sentiment_analysis.get('intensity', 0)}. For Phase 2, always routing to normal agent."
        }
        
        # Step 3: Generate response using selected agent
        response = await self.normal_agent.generate_response(conversation_history)
        
        # Step 4: Prepare analysis data for API response
        analysis_data = {
            "sentiment_analysis": sentiment_analysis,
            "orchestrator_decision": orchestrator_thinking
        }
        
        return response, "normal", analysis_data 