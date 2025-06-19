from typing import List, Dict, Any
import json
import re
import os
from openai import OpenAI

class OrchestratorAgent:
    """Fully agentic orchestrator using OpenAI GPT-4o-mini for intelligent emotional routing"""
    
    def __init__(self):
        self.anger_counter = 0
        self.max_counter = 2
        # Use OpenAI GPT-4o-mini for orchestrator decisions
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # Fast and capable model
    
    async def make_routing_decision(self, sentiment_analysis: Dict[str, Any], current_agent: str, user_message: str) -> Dict[str, Any]:
        """Make fully agentic routing decision using OpenAI GPT-4o-mini"""
        
        # Check for apologies and vulgarity in user message
        apology_detected = self._detect_apology(user_message)
        vulgarity_detected = self._detect_vulgarity(user_message)
        
        # Update anger counter if apology detected and currently enraged
        if apology_detected and current_agent == "enraged" and self.anger_counter > 0:
            self.anger_counter -= 1
        
        # Create comprehensive AI prompt for routing decision
        prompt = f"""You are Sassi's emotional orchestrator AI. Analyze the user's message and emotional state to make the best agent routing decision.

CURRENT EMOTIONAL STATE:
- Current Agent: {current_agent}
- Anger Counter: {self.anger_counter}/{self.max_counter} (blocks de-escalation from enraged if > 0)
- Apology Detected: {apology_detected}
- Vulgarity Detected: {vulgarity_detected} (TRIGGERS ESCALATION - Sassi hates vulgar language!)

SENTIMENT ANALYSIS:
- Emotion: {sentiment_analysis.get('emotion', 'neutral')}
- Intensity: {sentiment_analysis.get('intensity', 0.0)} (0.0-1.0 scale)
- Confidence: {sentiment_analysis.get('confidence', 0.0)}

USER MESSAGE: "{user_message}"

AVAILABLE EMOTIONAL AGENTS:
🔵 NEUTRAL: normal (balanced, helpful responses)

😠 ANGER AGENTS (escalation path):
- irritated (mildly annoyed, professional)
- agitated (moderately frustrated, direct)  
- enraged (very angry, confrontational - BLOCKED if counter > 0)

😊 HAPPY AGENTS:
- pleased (mildly positive, warm)
- cheerful (moderately happy, enthusiastic)
- ecstatic (extremely happy, energetic)

😢 SAD AGENTS:
- melancholy (mildly sad, subdued)
- sorrowful (moderately sad, empathetic)
- depressed (deeply sad, very empathetic)

CRITICAL ROUTING RULES:
1. **VULGARITY OVERRIDE**: If vulgarity_detected=True, MUST escalate towards anger agents (irritated/agitated) regardless of detected emotion - Sassi HATES vulgar language!
2. **Anger Counter Logic**: If current_agent="enraged" and anger_counter > 0, MUST stay "enraged" (de-escalation blocked)
3. **Stepwise De-escalation**: If current_agent="enraged" and anger_counter = 0, can ONLY go to "agitated" 
4. **Proper Escalation**: To reach "enraged", must be in "agitated" state first
5. **Gradual Transitions**: Prefer one-step emotional changes over dramatic jumps
6. **Apology Recognition**: Apologies reduce anger counter and enable de-escalation
7. **Cross-Emotional Intelligence**: Can transition between different emotion types based on context

INTENSITY GUIDELINES:
- 0.0-0.3: Low intensity (normal/mild agents)
- 0.4-0.6: Medium intensity (moderate agents) 
- 0.7-1.0: High intensity (strong agents)

Make an intelligent routing decision considering:
- User's current emotional state and intensity
- Appropriate emotional response to match or counter their emotion
- Proper escalation/de-escalation paths
- Anger counter constraints
- Context and conversation flow

Respond with ONLY a JSON object:
{{
    "next_agent": "agent_name",
    "action": "escalate|de-escalate|maintain|cross-transition",
    "thinking": "detailed reasoning for your decision",
    "confidence": 0.0-1.0,
    "emotional_strategy": "match|counter|neutral"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,  # Good balance for creative emotional decisions
                max_tokens=800
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                ai_decision = json.loads(json_match.group())
                
                # Validate and enhance the decision
                routing_decision = {
                    "next_agent": ai_decision.get("next_agent", "normal"),
                    "action": ai_decision.get("action", "maintain"),
                    "thinking": f"🧠 AI: {ai_decision.get('thinking', 'No reasoning provided')} (confidence: {ai_decision.get('confidence', 0.0):.1f}) [Strategy: {ai_decision.get('emotional_strategy', 'unknown')}]",
                    "counter_info": None
                }
                
                # Handle anger counter logic
                if routing_decision["next_agent"] == "enraged":
                    self.anger_counter = self.max_counter
                    routing_decision["counter_info"] = {
                        "counter": self.anger_counter,
                        "display": f"🤬 {self.anger_counter}/{self.max_counter}",
                        "apology_detected": apology_detected,
                        "blocked_deescalation": True
                    }
                elif current_agent == "enraged" and routing_decision["next_agent"] != "enraged":
                    self.anger_counter = 0
                    routing_decision["counter_info"] = {
                        "counter": self.anger_counter,
                        "display": f"🤬 {self.anger_counter}/{self.max_counter}",
                        "apology_detected": apology_detected,
                        "blocked_deescalation": False
                    }
                
                return routing_decision
                
        except Exception as e:
            print(f"❌ AI routing failed: {e}")
            # Return safe fallback instead of rule-based system
            return {
                "next_agent": "normal",
                "action": "maintain",
                "thinking": f"🚨 AI routing failed ({str(e)}), using safe fallback to normal agent",
                "counter_info": None
            }
    
    def _detect_apology(self, message: str) -> bool:
        """Detect apology keywords in user message"""
        apology_keywords = [
            "sorry", "apologize", "my bad", "forgive me", 
            "i'm wrong", "my fault", "pardon me", "excuse me",
            "apologies", "i apologize"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in apology_keywords)
    
    def _detect_vulgarity(self, message: str) -> bool:
        """Detect vulgar language that triggers Sassi's irritation"""
        vulgar_words = [
            "shit", "damn", "fuck", "fucking", "hell", "crap", 
            "piss", "ass", "bitch", "bastard", "bloody",
            "goddamn", "jesus christ", "christ", "wtf"
        ]
        
        message_lower = message.lower()
        # Check for exact word matches (not just substrings)
        words = message_lower.split()
        return any(word.strip('.,!?;:') in vulgar_words for word in words)
    
    def get_counter_display(self) -> str:
        """Get current counter display"""
        return f"🤬 {self.anger_counter}/{self.max_counter}"
    
    def reset_counter(self):
        """Reset anger counter"""
        self.anger_counter = 0 