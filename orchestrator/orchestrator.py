from typing import List, Dict, Any, Tuple
from agents.normal_agent import NormalAgent
from agents.sentiment_agent import SentimentAgent
from agents.happy_level1_pleased_agent import HappyLevel1PleasedAgent
from agents.happy_level2_cheerful_agent import HappyLevel2CheerfulAgent
from agents.happy_level3_ecstatic_agent import HappyLevel3EcstaticAgent
from agents.sad_level1_melancholy_agent import SadLevel1MelancholyAgent
from agents.sad_level2_sorrowful_agent import SadLevel2SorrowfulAgent
from agents.sad_level3_depressed_agent import SadLevel3DepressedAgent
from agents.angry_level1_irritated_agent import AngryLevel1IrritatedAgent
from agents.angry_level2_agitated_agent import AngryLevel2AgitatedAgent
from agents.angry_level3_enraged_agent import AngryLevel3EnragedAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.base_agent import ChatMessage
from utils.anger_meter import AngerMeter

class Orchestrator:
    """Enhanced orchestrator that manages conversation flow with sentiment analysis"""
    
    def __init__(self):
        self.normal_agent = NormalAgent()
        self.sentiment_agent = SentimentAgent()
        self.orchestrator_agent = OrchestratorAgent()
        # Happy agents
        self.happy_level1_pleased_agent = HappyLevel1PleasedAgent()
        self.happy_level2_cheerful_agent = HappyLevel2CheerfulAgent()
        self.happy_level3_ecstatic_agent = HappyLevel3EcstaticAgent()
        # Sad agents
        self.sad_level1_melancholy_agent = SadLevel1MelancholyAgent()
        self.sad_level2_sorrowful_agent = SadLevel2SorrowfulAgent()
        self.sad_level3_depressed_agent = SadLevel3DepressedAgent()
        # Angry agents
        self.angry_level1_irritated_agent = AngryLevel1IrritatedAgent()
        self.angry_level2_agitated_agent = AngryLevel2AgitatedAgent()
        self.angry_level3_enraged_agent = AngryLevel3EnragedAgent()
        self.current_agent = "normal"
        self.conversation_state = {}
        self.emotional_history = []  # Track emotional trajectory
        
        # Initialize anger meter system
        self.anger_meter = AngerMeter()
    
    async def process_message(self, message: str, conversation_history: List[ChatMessage]) -> Tuple[str, str, Dict[str, Any]]:
        """
        Process user message and return response with agent type and sentiment analysis
        
        Returns:
            Tuple of (response, agent_type, analysis_data)
        """
        
        # Step 1: Analyze sentiment
        sentiment_analysis = await self.sentiment_agent.analyze_sentiment(message)
        
        # Step 2: Process anger meter for anger-related emotions
        anger_emotions = ['anger', 'frustration', 'irritation', 'rage', 'annoyance']
        emotion = sentiment_analysis.get('emotion', 'neutral')
        
        if emotion in anger_emotions:
            # Use anger meter system for anger routing
            anger_agent, anger_meter_info = self.anger_meter.process_message(message, sentiment_analysis)
            next_agent = anger_agent
            
            # Create orchestrator thinking for anger meter decision
            orchestrator_thinking = {
                "current_agent": self.current_agent,
                "next_agent": next_agent,
                "action": "anger_meter_routing",
                "thinking": f"Anger meter system activated. Current anger points: {anger_meter_info['anger_points']}, routing to {anger_agent} agent.",
                "emotion_detected": emotion,
                "intensity_detected": sentiment_analysis.get('intensity', 0),
                "anger_meter": anger_meter_info
            }
        else:
            # Use original orchestrator logic for non-anger emotions
            routing_decision = await self.orchestrator_agent.make_routing_decision(
                sentiment_analysis, self.current_agent, message
            )
            next_agent = routing_decision.get("next_agent", "normal")
            orchestrator_thinking = routing_decision
            
            # Apply anger meter decay for non-anger messages
            _, anger_meter_info = self.anger_meter.process_message(message, sentiment_analysis)
            orchestrator_thinking["anger_meter"] = anger_meter_info
        
        # Step 3: Generate enhanced orchestrator insights
        orchestrator_insights = self._generate_insights(sentiment_analysis, orchestrator_thinking, message)
        
        # Step 4: Generate response using selected agent
        response = await self._get_agent_response(next_agent, conversation_history, orchestrator_thinking)
        
        # Step 5: Update emotional history and current agent
        self._update_emotional_history(sentiment_analysis, next_agent)
        self.current_agent = next_agent
        
        # Step 6: Prepare analysis data for API response
        analysis_data = {
            "sentiment_analysis": sentiment_analysis,
            "orchestrator_decision": orchestrator_thinking,
            "orchestrator_insights": orchestrator_insights
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
        
        # Angry emotion routing (anger, frustration, irritation, rage)
        elif emotion in ['anger', 'frustration', 'irritation', 'rage', 'annoyance']:
            if intensity >= 0.8:  # Enraged level (0.8-1.0)
                next_agent = "enraged"
                action = "escalate" if self.current_agent != "enraged" else "maintain"
                thinking = f"High anger intensity ({intensity:.1f}/1.0) detected. Routing to enraged agent for intense anger expression."
            elif intensity >= 0.5:  # Agitated level (0.5-0.7)
                next_agent = "agitated"
                action = "escalate" if self.current_agent in ["normal", "irritated"] else "de-escalate" if self.current_agent == "enraged" else "maintain"
                thinking = f"Moderate anger intensity ({intensity:.1f}/1.0) detected. Routing to agitated agent for frustrated response."
            elif intensity >= 0.3:  # Irritated level (0.3-0.4)
                next_agent = "irritated"
                action = "escalate" if self.current_agent == "normal" else "de-escalate" if self.current_agent in ["agitated", "enraged"] else "maintain"
                thinking = f"Mild anger intensity ({intensity:.1f}/1.0) detected. Routing to irritated agent for annoyed response."
            else:  # Low anger (0.1-0.2) - stay normal
                next_agent = "normal"
                action = "de-escalate" if self.current_agent != "normal" else "maintain"
                thinking = f"Low anger intensity ({intensity:.1f}/1.0) detected. Staying with normal agent."
        
        else:
            # For other emotions, use normal agent
            next_agent = "normal"
            action = "de-escalate" if self.current_agent != "normal" else "maintain"
            thinking = f"Emotion '{emotion}' detected with intensity {intensity:.1f}/1.0. Using normal agent (other emotional agents not yet implemented)."
        
        orchestrator_thinking = {
            "current_agent": self.current_agent,
            "next_agent": next_agent,
            "action": action,
            "thinking": thinking,
            "emotion_detected": emotion,
            "intensity_detected": intensity
        }
        
        return next_agent, orchestrator_thinking
    
    async def _get_agent_response(self, agent_name: str, conversation_history: List[ChatMessage], orchestrator_thinking: Dict[str, Any] = None) -> str:
        """Get response from the specified agent"""
        
        # Universal instruction for all agents to use <t></t> tags
        universal_instruction = ChatMessage(
            role="system",
            content="You will use <t></t> tags"
        )
        
        # Add universal instruction to all agents
        enhanced_history = conversation_history + [universal_instruction]
        
        # Happy agents
        if agent_name == "pleased":
            return await self.happy_level1_pleased_agent.generate_response(enhanced_history)
        elif agent_name == "cheerful":
            return await self.happy_level2_cheerful_agent.generate_response(enhanced_history)
        elif agent_name == "ecstatic":
            return await self.happy_level3_ecstatic_agent.generate_response(enhanced_history)
        # Sad agents
        elif agent_name == "melancholy":
            return await self.sad_level1_melancholy_agent.generate_response(enhanced_history)
        elif agent_name == "sorrowful":
            return await self.sad_level2_sorrowful_agent.generate_response(enhanced_history)
        elif agent_name == "depressed":
            return await self.sad_level3_depressed_agent.generate_response(enhanced_history)
        # Angry agents
        elif agent_name == "irritated":
            return await self.angry_level1_irritated_agent.generate_response(enhanced_history)
        elif agent_name == "agitated":
            return await self.angry_level2_agitated_agent.generate_response(enhanced_history)
        elif agent_name == "enraged":
            # Use anger meter data for dynamic counter display
            anger_meter_info = orchestrator_thinking.get("anger_meter", {})
            anger_points = anger_meter_info.get("anger_points", 100)
            max_points = anger_meter_info.get("max_points", 100)
            
            # Calculate dynamic anger level (0-3 scale for display)
            anger_percentage = anger_points / max_points
            if anger_percentage >= 0.9:
                counter_level = 3
            elif anger_percentage >= 0.7:
                counter_level = 2
            else:
                counter_level = 1
                
            counter_display = f"🔥 {int(anger_points)}/{max_points} pts (LVL {counter_level})"
            
            # Create a system message with dynamic anger meter info (in addition to universal instruction)
            counter_context = ChatMessage(
                role="system",
                content=f"""
DYNAMIC ANGER METER DISPLAY: {counter_display}

CRITICAL INSTRUCTIONS:
- You MUST start your response with: <t>{counter_display} [your thoughts]</t>
- NEVER skip the anger meter display
- Use the EXACT format: <t>{counter_display} [YOUR ANGRY THOUGHTS IN ALL CAPS]</t>
- Then follow with your ALL-CAPS vulgar response
- The anger meter shows your ACTUAL accumulated rage from the conversation
- Higher points = more intense anger and vulgarity
- Level {counter_level} rage intensity - respond accordingly
"""
            )
            # For enraged agent, add both universal instruction and specific counter context
            enraged_enhanced_history = conversation_history + [universal_instruction, counter_context]
            return await self.angry_level3_enraged_agent.generate_response(enraged_enhanced_history)
        else:  # Default to normal agent
            return await self.normal_agent.generate_response(enhanced_history)
    
    def _generate_insights(self, sentiment_analysis: Dict[str, Any], orchestrator_thinking: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Generate enhanced orchestrator insights"""
        emotion = sentiment_analysis.get('emotion', 'neutral')
        intensity = sentiment_analysis.get('intensity', 0)
        current_agent = orchestrator_thinking.get('current_agent', 'normal')
        next_agent = orchestrator_thinking.get('next_agent', 'normal')
        action = orchestrator_thinking.get('action', 'maintain')
        
        # Generate conversation trajectory
        trajectory = self._get_conversation_trajectory()
        
        # Extract detected triggers
        triggers = sentiment_analysis.get('emotional_indicators', [])
        
        # Generate state transition explanation
        state_transition = self._explain_state_transition(current_agent, next_agent, action, intensity)
        
        # Generate orchestrator suggestion
        suggestion = self._generate_orchestrator_suggestion(next_agent, emotion, intensity, action)
        
        # Create trigger explanation
        trigger_explanation = self._explain_triggers(triggers, emotion, intensity, message)
        
        return {
            "current_state": f"{current_agent} → {next_agent}",
            "emotional_intensity": f"{intensity:.1f}/1.0 ({self._intensity_description(intensity)})",
            "trigger_explanation": trigger_explanation,
            "conversation_trajectory": trajectory,
            "detected_triggers": triggers,
            "state_transition": state_transition,
            "orchestrator_suggestion": suggestion
        }
    
    def _update_emotional_history(self, sentiment_analysis: Dict[str, Any], agent: str):
        """Update emotional history for trajectory tracking"""
        emotion = sentiment_analysis.get('emotion', 'neutral')
        intensity = sentiment_analysis.get('intensity', 0)
        
        # Keep last 5 emotional states for trajectory
        self.emotional_history.append({
            "emotion": emotion,
            "intensity": intensity,
            "agent": agent
        })
        
        if len(self.emotional_history) > 5:
            self.emotional_history.pop(0)
    
    def _get_conversation_trajectory(self) -> str:
        """Generate conversation trajectory description"""
        if len(self.emotional_history) < 2:
            return "Initial conversation state"
        
        # Get last few states
        recent_states = self.emotional_history[-3:] if len(self.emotional_history) >= 3 else self.emotional_history
        
        trajectory_parts = []
        for state in recent_states:
            emotion_desc = f"{state['emotion']}({state['intensity']:.1f})"
            trajectory_parts.append(f"{state['agent']}[{emotion_desc}]")
        
        trajectory = " → ".join(trajectory_parts)
        
        # Add trend analysis
        if len(self.emotional_history) >= 2:
            prev_intensity = self.emotional_history[-2]['intensity']
            curr_intensity = self.emotional_history[-1]['intensity']
            
            if curr_intensity > prev_intensity + 0.1:
                trend = " (escalating)"
            elif curr_intensity < prev_intensity - 0.1:
                trend = " (de-escalating)"
            else:
                trend = " (stable)"
            
            trajectory += trend
        
        return trajectory
    
    def _intensity_description(self, intensity: float) -> str:
        """Convert intensity to descriptive text"""
        if intensity >= 0.8:
            return "very strong emotion"
        elif intensity >= 0.5:
            return "moderate emotion"
        elif intensity >= 0.3:
            return "mild emotion"
        elif intensity >= 0.1:
            return "subtle emotion"
        else:
            return "minimal emotion"
    
    def _explain_state_transition(self, current: str, next_agent: str, action: str, intensity: float) -> str:
        """Explain why the state transition occurred"""
        if action == "escalate":
            return f"Escalating from {current} to {next_agent} due to intensity {intensity:.1f} requiring more emotional engagement"
        elif action == "de-escalate":
            return f"De-escalating from {current} to {next_agent} as intensity {intensity:.1f} suggests calmer response needed"
        elif action == "maintain":
            return f"Maintaining {current} agent as intensity {intensity:.1f} is appropriate for current emotional level"
        else:
            return f"Transitioning from {current} to {next_agent} based on emotional context"
    
    def _explain_triggers(self, triggers: List[str], emotion: str, intensity: float, message: str) -> str:
        """Explain what triggered the emotional detection"""
        if not triggers:
            return f"Detected {emotion} emotion through overall message tone and context"
        
        trigger_text = ", ".join(f"'{trigger}'" for trigger in triggers[:3])  # Limit to first 3
        
        return f"Key phrases {trigger_text} indicate {emotion} emotion with {intensity:.1f} intensity"
    
    def _generate_orchestrator_suggestion(self, agent: str, emotion: str, intensity: float, action: str) -> str:
        """Generate orchestrator's reasoning and suggestion"""
        agent_descriptions = {
            "normal": "balanced, professional responses for neutral emotions",
            "pleased": "gentle positivity and contentment for mild happiness",
            "cheerful": "upbeat enthusiasm and energy for moderate happiness", 
            "ecstatic": "overwhelming joy and celebration for intense happiness",
            "melancholy": "gentle, wistful sadness and contemplative responses for mild sadness",
            "sorrowful": "deeper emotional weight and vulnerability for moderate sadness",
            "depressed": "profound sadness and emotional struggle for intense sadness",
            "irritated": "mild annoyance and impatience for low-level anger",
            "agitated": "clear frustration and agitation for moderate anger",
            "enraged": "intense fury and hostility for high-level anger"
        }
        
        agent_desc = agent_descriptions.get(agent, "appropriate emotional response")
        
        if emotion in ['joy', 'happiness', 'excitement', 'enthusiasm']:
            return f"Using {agent} agent for {agent_desc}. Intensity {intensity:.1f} matches {agent} emotional range perfectly."
        elif emotion in ['anger', 'frustration', 'irritation', 'rage', 'annoyance']:
            return f"Using {agent} agent for {agent_desc}. Intensity {intensity:.1f} requires appropriate anger expression and venting."
        else:
            return f"Using {agent} agent for {agent_desc}. Emotion '{emotion}' requires measured, supportive response."
    
    def reset_state(self):
        """Reset orchestrator to initial state"""
        self.current_agent = "normal"
        self.conversation_state = {}
        self.emotional_history = []
        self.anger_meter.reset_meter()
        self.orchestrator_agent.reset_counter()