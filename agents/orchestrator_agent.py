from typing import List, Dict, Any
import json
import re

class OrchestratorAgent:
    """Orchestrator agent that uses prompt-based routing with anger counter system"""
    
    def __init__(self):
        self.anger_counter = 0
        self.max_counter = 2
    
    async def make_routing_decision(self, sentiment_analysis: Dict[str, Any], current_agent: str, user_message: str) -> Dict[str, Any]:
        """Make routing decision based on sentiment analysis and current state"""
        
        # Check for apologies in user message
        apology_detected = self._detect_apology(user_message)
        
        # Update anger counter if apology detected and currently enraged
        if apology_detected and current_agent == "enraged" and self.anger_counter > 0:
            self.anger_counter -= 1
        
        # Get emotion and intensity
        emotion = sentiment_analysis.get('emotion', 'neutral')
        intensity = sentiment_analysis.get('intensity', 0.0)
        
        # Initialize routing decision
        routing_decision = {
            "next_agent": "normal",
            "action": "maintain",
            "thinking": "",
            "counter_info": None
        }
        
        # CRITICAL: If currently enraged and counter > 0, BLOCK all de-escalation
        if current_agent == "enraged" and self.anger_counter > 0:
            routing_decision.update({
                "next_agent": "enraged",
                "action": "maintain",
                "thinking": f"De-escalation blocked by anger counter ({self.anger_counter}/{self.max_counter}). Must stay enraged until counter reaches 0.",
                "counter_info": {
                    "counter": self.anger_counter,
                    "display": f"🤬 {self.anger_counter}/{self.max_counter}",
                    "apology_detected": apology_detected,
                    "blocked_deescalation": True
                }
            })
            return routing_decision
        
        # SPECIAL CASE: If currently enraged and counter == 0, ONLY allow stepwise de-escalation to agitated
        if current_agent == "enraged" and self.anger_counter == 0:
            routing_decision.update({
                "next_agent": "agitated",
                "action": "de-escalate",
                "thinking": f"Anger counter reached 0/2. Stepwise de-escalation from enraged to agitated only.",
                "counter_info": {
                    "counter": self.anger_counter,
                    "display": f"🤬 {self.anger_counter}/{self.max_counter}",
                    "apology_detected": apology_detected,
                    "blocked_deescalation": False
                }
            })
            # Reset counter when leaving enraged
            self.anger_counter = 0
            return routing_decision
        
        # Normal routing logic (only if not blocked by counter)
        if emotion in ['anger', 'frustration', 'irritation', 'rage', 'annoyance']:
            if intensity >= 0.8 and current_agent == "agitated":  # Can only reach enraged from agitated
                routing_decision.update({
                    "next_agent": "enraged",
                    "action": "escalate",
                    "thinking": f"Extreme anger intensity ({intensity:.1f}) from agitated state. Escalating to enraged with counter initialized."
                })
                # Initialize counter for enraged state
                self.anger_counter = self.max_counter
                routing_decision["counter_info"] = {
                    "counter": self.anger_counter,
                    "display": f"🤬 {self.anger_counter}/{self.max_counter}",
                    "apology_detected": apology_detected,
                    "blocked_deescalation": self.anger_counter > 0
                }
            elif intensity >= 0.8 and current_agent != "agitated":  # High intensity but not from agitated
                routing_decision.update({
                    "next_agent": "agitated",
                    "action": "escalate" if current_agent in ["normal", "irritated"] else "maintain",
                    "thinking": f"High anger intensity ({intensity:.1f}) detected, but must progress through agitated first."
                })
            elif intensity >= 0.5:  # Agitated level
                routing_decision.update({
                    "next_agent": "agitated",
                    "action": "escalate" if current_agent in ["normal", "irritated"] else "maintain",
                    "thinking": f"Moderate anger intensity ({intensity:.1f}) detected. Routing to agitated agent."
                })
            elif intensity >= 0.3:  # Irritated level
                # Enforce stepwise de-escalation: agitated can only go to irritated, not from enraged
                if current_agent == "agitated":
                    routing_decision.update({
                        "next_agent": "irritated",
                        "action": "de-escalate",
                        "thinking": f"Mild anger intensity ({intensity:.1f}) detected. Stepwise de-escalation from agitated to irritated."
                    })
                elif current_agent == "normal":
                    routing_decision.update({
                        "next_agent": "irritated",
                        "action": "escalate",
                        "thinking": f"Mild anger intensity ({intensity:.1f}) detected. Escalating from normal to irritated."
                    })
                else:  # irritated or other states
                    routing_decision.update({
                        "next_agent": "irritated",
                        "action": "maintain",
                        "thinking": f"Mild anger intensity ({intensity:.1f}) detected. Maintaining irritated agent."
                    })
            else:  # Low anger
                # Enforce stepwise de-escalation: only allow one step down
                if current_agent == "irritated":
                    routing_decision.update({
                        "next_agent": "normal",
                        "action": "de-escalate",
                        "thinking": f"Low anger intensity ({intensity:.1f}) detected. Stepwise de-escalation from irritated to normal."
                    })
                elif current_agent == "agitated":
                    routing_decision.update({
                        "next_agent": "irritated",
                        "action": "de-escalate",
                        "thinking": f"Low anger intensity ({intensity:.1f}) detected. Stepwise de-escalation from agitated to irritated."
                    })
                else:  # normal or other states
                    routing_decision.update({
                        "next_agent": "normal",
                        "action": "maintain",
                        "thinking": f"Low anger intensity ({intensity:.1f}) detected. Using normal agent."
                    })
        
        elif emotion in ['joy', 'happiness', 'excitement', 'enthusiasm']:
            # Happy emotion routing
            if intensity >= 0.8:
                routing_decision.update({
                    "next_agent": "ecstatic",
                    "action": "escalate" if current_agent != "ecstatic" else "maintain",
                    "thinking": f"High happiness intensity ({intensity:.1f}) detected. Routing to ecstatic agent."
                })
            elif intensity >= 0.5:
                routing_decision.update({
                    "next_agent": "cheerful",
                    "action": "escalate" if current_agent in ["normal", "pleased"] else "de-escalate" if current_agent == "ecstatic" else "maintain",
                    "thinking": f"Moderate happiness intensity ({intensity:.1f}) detected. Routing to cheerful agent."
                })
            elif intensity >= 0.3:
                routing_decision.update({
                    "next_agent": "pleased",
                    "action": "escalate" if current_agent == "normal" else "de-escalate" if current_agent in ["cheerful", "ecstatic"] else "maintain",
                    "thinking": f"Mild happiness intensity ({intensity:.1f}) detected. Routing to pleased agent."
                })
            else:
                routing_decision.update({
                    "next_agent": "normal",
                    "action": "de-escalate" if current_agent != "normal" else "maintain",
                    "thinking": f"Low happiness intensity ({intensity:.1f}) detected. Staying with normal agent."
                })
        
        else:
            # Neutral or other emotions - enforce stepwise de-escalation
            if current_agent == "agitated":
                routing_decision.update({
                    "next_agent": "irritated",
                    "action": "de-escalate",
                    "thinking": f"Neutral emotion '{emotion}' with intensity {intensity:.1f} detected. Stepwise de-escalation from agitated to irritated."
                })
            elif current_agent == "irritated":
                routing_decision.update({
                    "next_agent": "normal",
                    "action": "de-escalate",
                    "thinking": f"Neutral emotion '{emotion}' with intensity {intensity:.1f} detected. Stepwise de-escalation from irritated to normal."
                })
            else:
                routing_decision.update({
                    "next_agent": "normal",
                    "action": "maintain" if current_agent == "normal" else "de-escalate",
                    "thinking": f"Neutral emotion '{emotion}' with intensity {intensity:.1f} detected. Using normal agent."
                })
        
        # If transitioning away from enraged, reset counter
        if current_agent == "enraged" and routing_decision["next_agent"] != "enraged":
            self.anger_counter = 0
        
        return routing_decision
    
    def _detect_apology(self, message: str) -> bool:
        """Detect apology keywords in user message"""
        apology_keywords = [
            "sorry", "apologize", "my bad", "forgive me", 
            "i'm wrong", "my fault", "pardon me", "excuse me",
            "apologies", "i apologize"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in apology_keywords)
    

    
    def get_counter_display(self) -> str:
        """Get current counter display"""
        return f"🤬 {self.anger_counter}/{self.max_counter}"
    
    def reset_counter(self):
        """Reset anger counter"""
        self.anger_counter = 0 