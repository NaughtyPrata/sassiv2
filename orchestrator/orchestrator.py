from typing import List, Dict, Any, Tuple
import asyncio
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
        self.ended = False  # Track if conversation is ended by bye detector
    
    def _bye_detector(self, text: str) -> bool:
        """Detect if the agent is saying goodbye/walking away"""
        bye_phrases = [
            "bye", "goodbye", "i'm done", "i am done", "i'm leaving", "i am leaving", "i'm out", "i am out", "that's it", "i'm finished", "i am finished"
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in bye_phrases)
    
    async def process_message_combined(self, message: str, conversation_history: List[ChatMessage]) -> Tuple[str, str, Dict[str, Any]]:
        """
        Process user message using combined sentiment+response approach (faster)
        
        Returns:
            Tuple of (response, agent_type, analysis_data)
        """
        if self.ended:
            return "[Conversation ended. Please reset to start a new chat.]", self.current_agent, {"ended": True}
        
        # For performance, use traditional sentiment analysis first, then get appropriate agent response
        # This still reduces 3 API calls to 2 while maintaining accuracy
        sentiment_analysis = await self.sentiment_agent.analyze_sentiment(message)
        
        # Process anger meter 
        anger_emotions = ['anger', 'frustration', 'irritation', 'rage', 'annoyance']
        emotion = sentiment_analysis.get('emotion', 'neutral')
        
        # Check if we need to route to angry agent based on anger meter
        anger_agent, anger_meter_info = self.anger_meter.process_message(message, sentiment_analysis)
        
        # Create orchestrator thinking first
        orchestrator_thinking = {
            "current_agent": self.current_agent,
            "next_agent": "normal",  # Will be updated below
            "action": "combined_approach",
            "thinking": f"Combined sentiment+response approach. Detected {emotion} with intensity {sentiment_analysis.get('intensity', 0):.1f}",
            "emotion_detected": emotion,
            "intensity_detected": sentiment_analysis.get('intensity', 0),
            "anger_meter": anger_meter_info
        }
        
        if anger_agent != "normal":
            # Use angry agent
            next_agent = anger_agent
            orchestrator_thinking["next_agent"] = next_agent
            response = await self._get_agent_response(anger_agent, conversation_history, orchestrator_thinking)
        elif emotion in anger_emotions:
            # If emotion is angry but anger meter says normal, still use appropriate level
            if sentiment_analysis.get('intensity', 0) >= 0.7:
                next_agent = "enraged"
            elif sentiment_analysis.get('intensity', 0) >= 0.4:
                next_agent = "agitated"  
            else:
                next_agent = "irritated"
            orchestrator_thinking["next_agent"] = next_agent
            response = await self._get_agent_response(next_agent, conversation_history, orchestrator_thinking)
        else:
            # Use normal agent
            next_agent = "normal"
            orchestrator_thinking["next_agent"] = next_agent
            response = await self._get_agent_response(next_agent, conversation_history, orchestrator_thinking)
        
        # Generate insights
        orchestrator_insights = self._generate_insights(sentiment_analysis, orchestrator_thinking, message)
        
        # Check for walkaway/bye conditions
        if next_agent == "enraged":
            anger_points = anger_meter_info.get("anger_points", 0)
            max_points = anger_meter_info.get("max_points", 100)
            if anger_points >= max_points:
                self.ended = True
                walkaway_msg = "<t>🔥 {}/{} pts (LVL 3) I'M DONE WITH THIS. WALKING AWAY.</t>BYE. I'M OUT. CONVERSATION OVER.".format(int(anger_points), max_points)
                return walkaway_msg, next_agent, {"ended": True, "walkaway": True}
        
        if self._bye_detector(response):
            self.ended = True
            return response, next_agent, {"ended": True}
        
        # Update state
        self._update_emotional_history(sentiment_analysis, next_agent)
        self.current_agent = next_agent
        
        # Prepare analysis data
        analysis_data = {
            "sentiment_analysis": sentiment_analysis,
            "orchestrator_decision": orchestrator_thinking,
            "orchestrator_insights": orchestrator_insights
        }
        
        return response, next_agent, analysis_data

    async def process_message(self, message: str, conversation_history: List[ChatMessage]) -> Tuple[str, str, Dict[str, Any]]:
        """
        Process user message and return response with agent type and sentiment analysis
        
        Returns:
            Tuple of (response, agent_type, analysis_data)
        """
        
        if self.ended:
            return "[Conversation ended. Please reset to start a new chat.]", self.current_agent, {"ended": True}
        
        # Step 1: Run sentiment analysis and routing decision in parallel
        sentiment_task = asyncio.create_task(self.sentiment_agent.analyze_sentiment(message))
        
        # We need sentiment for routing, so we'll do a quick pre-analysis or run them sequentially
        # For now, let's do sentiment first, then parallel routing + response generation
        sentiment_analysis = await sentiment_task
        
        # Step 2: ALWAYS process anger meter first (anger persists across messages)
        anger_emotions = ['anger', 'frustration', 'irritation', 'rage', 'annoyance']
        emotion = sentiment_analysis.get('emotion', 'neutral')
        
        # ALWAYS use anger meter system - anger persists regardless of current message emotion
        anger_agent, anger_meter_info = self.anger_meter.process_message(message, sentiment_analysis)
        next_agent = anger_agent
        
        # Determine routing reason
        if emotion in anger_emotions:
            action = "anger_meter_routing_angry"
            thinking = f"Angry message detected. Anger meter: {anger_meter_info['anger_points']} pts, routing to {anger_agent} agent."
        else:
            action = "anger_meter_routing_persistent" 
            thinking = f"Non-angry message but anger persists. Anger meter: {anger_meter_info['anger_points']} pts, routing to {anger_agent} agent."
        
        # Create orchestrator thinking for anger meter decision
        orchestrator_thinking = {
            "current_agent": self.current_agent,
            "next_agent": next_agent,
            "action": action,
            "thinking": thinking,
            "emotion_detected": emotion,
            "intensity_detected": sentiment_analysis.get('intensity', 0),
            "anger_meter": anger_meter_info
        }
        
        # Step 3: Generate response and insights in parallel
        # ENRAGED MAX: If in enraged and anger meter is max, walk away
        if next_agent == "enraged":
            anger_points = anger_meter_info.get("anger_points", 0)
            max_points = anger_meter_info.get("max_points", 100)
            if anger_points >= max_points:
                self.ended = True
                walkaway_msg = "<t>🔥 {}/{} pts (LVL 3) I'M DONE WITH THIS. WALKING AWAY.</t>BYE. I'M OUT. CONVERSATION OVER.".format(int(anger_points), max_points)
                return walkaway_msg, next_agent, {"ended": True, "walkaway": True}
        
        # Run response generation and insights generation in parallel
        response_task = asyncio.create_task(self._get_agent_response(next_agent, conversation_history, orchestrator_thinking))
        insights_task = asyncio.create_task(asyncio.to_thread(self._generate_insights, sentiment_analysis, orchestrator_thinking, message))
        
        response, orchestrator_insights = await asyncio.gather(response_task, insights_task)
        
        # BYE DETECTOR: If agent says goodbye, end conversation
        if self._bye_detector(response):
            self.ended = True
            return response, next_agent, {"ended": True}
        
        # Step 5: Update emotional history and current agent
        # ENFORCE: No direct high-anger → normal transitions
        if self.current_agent == "agitated" and next_agent == "normal":
            orchestrator_thinking["thinking"] += " [RULE ENFORCED: Cannot move directly from agitated to normal. Routing to irritated instead.]"
            next_agent = "irritated"
            orchestrator_thinking["next_agent"] = "irritated"
            orchestrator_thinking["action"] = "de-escalate"
        elif self.current_agent == "enraged" and next_agent == "normal":
            orchestrator_thinking["thinking"] += " [RULE ENFORCED: Cannot move directly from enraged to normal. Routing to agitated instead.]"
            next_agent = "agitated"
            orchestrator_thinking["next_agent"] = "agitated"
            orchestrator_thinking["action"] = "de-escalate"
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
    
    async def _get_combined_sentiment_and_response(self, agent_name: str, message: str, conversation_history: List[ChatMessage], orchestrator_thinking: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        """Get sentiment analysis and agent response in a single API call"""
        # Get the agent to use
        if agent_name == "pleased":
            agent = self.happy_level1_pleased_agent
        elif agent_name == "cheerful":
            agent = self.happy_level2_cheerful_agent
        elif agent_name == "ecstatic":
            agent = self.happy_level3_ecstatic_agent
        elif agent_name == "melancholy":
            agent = self.sad_level1_melancholy_agent
        elif agent_name == "sorrowful":
            agent = self.sad_level2_sorrowful_agent
        elif agent_name == "depressed":
            agent = self.sad_level3_depressed_agent
        elif agent_name == "irritated":
            agent = self.angry_level1_irritated_agent
        elif agent_name == "agitated":
            agent = self.angry_level2_agitated_agent
        elif agent_name == "enraged":
            agent = self.angry_level3_enraged_agent
        else:
            agent = self.normal_agent
        
        # Create combined instruction
        combined_instruction = ChatMessage(
            role="system", 
            content=f"""You will respond in two parts:
1. SENTIMENT: Analyze the user's message for emotion, intensity (0.0-1.0), and emotional indicators
2. RESPONSE: Generate your character response using <t></t> tags

Format:
SENTIMENT: {{"emotion": "emotion_name", "intensity": 0.0, "emotional_indicators": ["word1", "word2"]}}
RESPONSE: <t>your thoughts</t>your response

User message to analyze: "{message}"
"""
        )
        
        enhanced_history = conversation_history + [combined_instruction]
        combined_result = await agent._call_groq(enhanced_history, max_tokens=2000)
        
        # Parse the combined result
        try:
            parts = combined_result.split("RESPONSE:", 1)
            sentiment_part = parts[0].replace("SENTIMENT:", "").strip()
            response_part = parts[1].strip() if len(parts) > 1 else combined_result
            
            # Parse sentiment JSON
            import json
            sentiment_analysis = json.loads(sentiment_part)
            sentiment_analysis.setdefault("confidence", 1.0)
            sentiment_analysis.setdefault("secondary_emotions", [])
            sentiment_analysis.setdefault("thinking", f"Combined analysis of user message for {agent_name} agent")
            
            return response_part, sentiment_analysis
        except:
            # Fallback: treat entire result as response, use default sentiment
            return combined_result, {
                "emotion": "neutral", "intensity": 0.0, "confidence": 1.0,
                "secondary_emotions": [], "emotional_indicators": [],
                "thinking": "Fallback sentiment analysis"
            }

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
        
        # Extract anger meter info if available
        anger_meter_data = orchestrator_thinking.get('anger_meter', {})
        
        return {
            "current_state": f"{current_agent} → {next_agent}",
            "emotional_intensity": f"{intensity:.1f}/1.0 ({self._intensity_description(intensity)})",
            "trigger_explanation": trigger_explanation,
            "conversation_trajectory": trajectory,
            "detected_triggers": triggers,
            "state_transition": state_transition,
            "orchestrator_suggestion": suggestion,
            "anger_points": anger_meter_data.get("anger_points", 0),
            "anger_level": anger_meter_data.get("anger_level", "normal"),
            "anger_thresholds": anger_meter_data.get("thresholds", {}),
            "anger_change_reasons": anger_meter_data.get("change_reasons", [])
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
        self.ended = False