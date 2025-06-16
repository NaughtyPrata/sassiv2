from typing import List, Dict, Any, Tuple
from agents.normal_agent import NormalAgent
from agents.sentiment_agent import SentimentAgent
from agents.pleased_agent import PleasedAgent
from agents.cheerful_agent import CheerfulAgent
from agents.ecstatic_agent import EcstaticAgent
from agents.base_agent import ChatMessage

class Orchestrator:
    """Enhanced orchestrator that manages conversation flow with sentiment analysis"""
    
    def __init__(self):
        self.normal_agent = NormalAgent()
        self.sentiment_agent = SentimentAgent()
        self.pleased_agent = PleasedAgent()
        self.cheerful_agent = CheerfulAgent()
        self.ecstatic_agent = EcstaticAgent()
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
        
        # Step 2: Make routing decision based on sentiment
        next_agent, orchestrator_thinking = self._determine_agent(sentiment_analysis)
        
        # Step 3: Generate response using selected agent
        response = await self._get_agent_response(next_agent, conversation_history)
        
        # Update current agent
        self.current_agent = next_agent
        
        # Step 4: Prepare analysis data for API response
        analysis_data = {
            "sentiment_analysis": sentiment_analysis,
            "orchestrator_decision": orchestrator_thinking
        }
        
        return response, next_agent, analysis_data
    
    def _determine_agent(self, sentiment_analysis: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Determine which agent to use based on sentiment analysis"""
        emotion = sentiment_analysis.get('emotion', 'neutral')
        intensity = sentiment_analysis.get('intensity', 0)
        
        # Happy emotion routing (joy, happiness, excitement, enthusiasm)
        if emotion in ['joy', 'happiness', 'excitement', 'enthusiasm']:
            if intensity >= 0.8:  # Ecstatic level (0.8-1.0)
                next_agent = "ecstatic"
                action = "escalate" if self.current_agent != "ecstatic" else "maintain"
                thinking = f"High happiness intensity ({intensity:.1f}/1.0) detected. Routing to ecstatic agent for maximum joy expression."
            elif intensity >= 0.5:  # Cheerful level (0.5-0.7)
                next_agent = "cheerful"
                action = "escalate" if self.current_agent in ["normal", "pleased"] else "de-escalate" if self.current_agent == "ecstatic" else "maintain"
                thinking = f"Moderate happiness intensity ({intensity:.1f}/1.0) detected. Routing to cheerful agent for upbeat response."
            elif intensity >= 0.3:  # Pleased level (0.3-0.4)
                next_agent = "pleased"
                action = "escalate" if self.current_agent == "normal" else "de-escalate" if self.current_agent in ["cheerful", "ecstatic"] else "maintain"
                thinking = f"Mild happiness intensity ({intensity:.1f}/1.0) detected. Routing to pleased agent for gentle positivity."
            else:  # Low happiness (0.1-0.2) - stay normal
                next_agent = "normal"
                action = "de-escalate" if self.current_agent != "normal" else "maintain"
                thinking = f"Low happiness intensity ({intensity:.1f}/1.0) detected. Staying with normal agent."
        else:
            # For non-happy emotions, use normal agent for now
            next_agent = "normal"
            action = "de-escalate" if self.current_agent != "normal" else "maintain"
            thinking = f"Non-happy emotion '{emotion}' detected with intensity {intensity:.1f}/1.0. Using normal agent (other emotional agents not yet implemented)."
        
        orchestrator_thinking = {
            "current_agent": self.current_agent,
            "next_agent": next_agent,
            "action": action,
            "thinking": thinking,
            "emotion_detected": emotion,
            "intensity_detected": intensity
        }
        
        return next_agent, orchestrator_thinking
    
    async def _get_agent_response(self, agent_name: str, conversation_history: List[ChatMessage]) -> str:
        """Get response from the specified agent"""
        if agent_name == "pleased":
            return await self.pleased_agent.generate_response(conversation_history)
        elif agent_name == "cheerful":
            return await self.cheerful_agent.generate_response(conversation_history)
        elif agent_name == "ecstatic":
            return await self.ecstatic_agent.generate_response(conversation_history)
        else:  # Default to normal agent
            return await self.normal_agent.generate_response(conversation_history)