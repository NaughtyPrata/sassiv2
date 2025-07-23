import yaml
import time
from typing import Dict, Any, Tuple, Optional
import re

class AngerMeter:
    """
    Anger meter system that tracks cumulative anger points over conversation.
    Points build up based on sentiment and decay over time/messages.
    """
    
    def __init__(self, config_path: str = "anger_config.yaml"):
        """Initialize anger meter with configuration"""
        self.config_path = config_path
        self.config = self._load_config()
        
        # Meter state
        self.anger_points = 0.0
        self.current_level = "normal"
        self.last_message_time = time.time()
        self.message_count = 0
        self.consecutive_anger_count = 0
        self.last_emotion = None
        self.escalation_cooldown_remaining = 0
        
        # De-escalation tracking (for enraged state)
        self.apology_count = 0
        self.recent_apologies = []  # Track recent apologies with message numbers
        self.enraged_de_escalation_blocked = False
        
        # History for debugging
        self.point_history = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return default config if file doesn't exist
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file is missing"""
        return {
            'anger_multiplier': 10.0,
            'thresholds': {'irritated': 20, 'agitated': 50, 'enraged': 80},
            'decay': {'idle_rate': 2, 'time_decay_enabled': False, 'time_rate': 0.5, 'minimum_floor': 0},
            'bonuses': {'consecutive_anger': 3, 'rapid_escalation': 2, 'vulgar_language': 5},
            'penalties': {'apology_reduction': -15, 'calm_language': -5, 'positive_emotion': -10},
            'meter': {'max_points': 100, 'escalation_cooldown': 2, 'de_escalation_immediate': True},
            'debug': {'show_meter_in_response': True, 'log_point_changes': True}
        }
    
    def process_message(self, message: str, sentiment_analysis: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Process a message and update anger meter.
        
        Args:
            message: User's message text
            sentiment_analysis: Sentiment data from sentiment agent
            
        Returns:
            Tuple of (agent_name, meter_info)
        """
        current_time = time.time()
        self.message_count += 1
        
        # Apply time-based decay if enabled
        if self.config['decay']['time_decay_enabled']:
            time_passed = (current_time - self.last_message_time) / 60  # minutes
            time_decay = time_passed * self.config['decay']['time_rate']
            self._adjust_points(-time_decay, "time_decay")
        
        # Calculate base points from sentiment
        emotion = sentiment_analysis.get('emotion', 'neutral')
        intensity = sentiment_analysis.get('intensity', 0.0)
        
        points_change = 0.0
        change_reasons = []
        
        # Check if this is an anger-related emotion OR contains vulgar/insulting language
        anger_emotions = ['anger', 'frustration', 'irritation', 'rage', 'annoyance']
        is_angry = emotion in anger_emotions
        has_vulgar_language = self._contains_vulgar_language(message)
        has_direct_insults = self._contains_direct_insults(message)
        
        # Force anger detection if vulgar/insulting language is present
        if has_vulgar_language or has_direct_insults:
            is_angry = True
            # Boost intensity if sentiment analysis missed the anger
            if emotion not in anger_emotions:
                intensity = max(intensity, 0.7)  # Force minimum anger intensity
                change_reasons.append("forced_anger_detection")
        
        if is_angry:
            # Reset apology count if user gets angry again (configurable)
            self._reset_apology_count_if_angry(True)
            
            # Base points from anger intensity
            base_points = intensity * self.config['anger_multiplier']
            points_change += base_points
            change_reasons.append(f"anger_base: +{base_points:.1f}")
            
            # Consecutive anger bonus
            if self.last_emotion in anger_emotions:
                self.consecutive_anger_count += 1
                bonus = self.config['bonuses']['consecutive_anger']
                points_change += bonus
                change_reasons.append(f"consecutive_anger: +{bonus}")
            else:
                self.consecutive_anger_count = 1
            
            # Check for vulgar language
            if self._contains_vulgar_language(message):
                vulgar_bonus = self.config['bonuses']['vulgar_language']
                points_change += vulgar_bonus
                change_reasons.append(f"vulgar_language: +{vulgar_bonus}")
            
            # Check for direct insults (bigger bonus)
            if self._contains_direct_insults(message):
                insult_bonus = self.config['bonuses']['direct_insults']
                points_change += insult_bonus
                change_reasons.append(f"direct_insults: +{insult_bonus}")
                
        else:
            # Not angry - apply decay and check for penalties
            self.consecutive_anger_count = 0
            
            # Idle decay
            idle_decay = self.config['decay']['idle_rate']
            points_change -= idle_decay
            change_reasons.append(f"idle_decay: -{idle_decay}")
            
            # Check for apology
            if self._contains_apology(message):
                apology_penalty = self.config['penalties']['apology_reduction']
                points_change += apology_penalty  # apology_reduction is negative
                change_reasons.append(f"apology: {apology_penalty}")
                
                # Track apology for de-escalation logic
                self._track_apology()
            
            # Check for positive emotions
            positive_emotions = ['joy', 'happiness', 'excitement', 'enthusiasm']
            if emotion in positive_emotions:
                positive_penalty = self.config['penalties']['positive_emotion']
                points_change += positive_penalty  # positive_emotion is negative
                change_reasons.append(f"positive_emotion: {positive_penalty}")
            
            # Check for calm language
            if self._contains_calm_language(message):
                calm_penalty = self.config['penalties']['calm_language']
                points_change += calm_penalty  # calm_language is negative
                change_reasons.append(f"calm_language: {calm_penalty}")
        
        # Apply points change
        self._adjust_points(points_change, ", ".join(change_reasons))
        
        # Determine agent based on current anger level (includes de-escalation blocking)
        new_agent = self._determine_agent()
        
        # Check if de-escalation was blocked/forced and add to change reasons
        if hasattr(self, '_de_escalation_blocked_this_message'):
            change_reasons.append(f"de_escalation_blocked: need {self._get_apologies_needed()} more apologies")
            delattr(self, '_de_escalation_blocked_this_message')
        elif hasattr(self, '_de_escalation_forced_this_message'):
            change_reasons.append(f"de_escalation_forced: {self.apology_count} apologies received")
            delattr(self, '_de_escalation_forced_this_message')
        
        # Update cooldown
        if self.escalation_cooldown_remaining > 0:
            self.escalation_cooldown_remaining -= 1
        
        # Update state
        self.last_emotion = emotion
        self.last_message_time = current_time
        
        # Prepare meter info for response
        meter_info = {
            "anger_points": round(self.anger_points, 1),
            "anger_level": new_agent,
            "points_change": round(points_change, 1),
            "change_reasons": change_reasons,
            "consecutive_anger": self.consecutive_anger_count,
            "message_count": self.message_count,
            "thresholds": self.config['thresholds'],
            "max_points": self.config['meter']['max_points']
        }
        
        # Add debug info if enabled
        if self.config['debug']['show_meter_in_response']:
            meter_info["debug"] = {
                "last_emotion": self.last_emotion,
                "escalation_cooldown": self.escalation_cooldown_remaining,
                "point_history": self.point_history[-5:],  # Last 5 changes
                "apology_count": self.apology_count,
                "apologies_needed": self._get_apologies_needed() if self.current_level == "enraged" else 0,
                "de_escalation_blocked": self.enraged_de_escalation_blocked
            }
        
        return new_agent, meter_info
    
    def _adjust_points(self, change: float, reason: str):
        """Adjust anger points and log the change"""
        old_points = self.anger_points
        self.anger_points += change
        
        # Apply bounds
        max_points = self.config['meter']['max_points']
        min_points = self.config['decay']['minimum_floor']
        self.anger_points = max(min_points, min(max_points, self.anger_points))
        
        # Log change if enabled
        if self.config['debug']['log_point_changes']:
            change_record = {
                "timestamp": time.time(),
                "old_points": round(old_points, 1),
                "new_points": round(self.anger_points, 1),
                "change": round(change, 1),
                "reason": reason
            }
            self.point_history.append(change_record)
            
            # Keep only last 20 records
            if len(self.point_history) > 20:
                self.point_history = self.point_history[-20:]
    
    def _determine_agent(self) -> str:
        """Determine which agent to use based on current anger points"""
        thresholds = self.config['thresholds']
        
        if self.anger_points >= thresholds['enraged']:
            new_level = "enraged"
        elif self.anger_points >= thresholds['agitated']:
            new_level = "agitated"
        elif self.anger_points >= thresholds['irritated']:
            new_level = "irritated"
        else:
            new_level = "normal"
        
        # ENFORCE GRADUAL ESCALATION: No direct jumps from normal to enraged
        current_rank = self._get_level_rank(self.current_level)
        new_rank = self._get_level_rank(new_level)
        
        if current_rank == 0 and new_rank == 3:  # normal (0) -> enraged (3)
            new_level = "agitated"  # Cap at agitated instead
        elif current_rank == 1 and new_rank == 3:  # irritated (1) -> enraged (3)  
            new_level = "agitated"  # Cap at agitated instead
        
        # Check escalation cooldown
        if (new_level != self.current_level and 
            self._get_level_rank(new_level) > self._get_level_rank(self.current_level) and
            self.escalation_cooldown_remaining > 0):
            # Still in cooldown, can't escalate
            new_level = self.current_level
        
        # Check de-escalation blocking/forcing for enraged state
        if self.current_level == "enraged":
            if self._can_de_escalate_from_enraged():
                # Force de-escalation with 2+ apologies, regardless of points
                if new_level == "enraged":
                    # Calculate what level they should be if not enraged
                    if self.anger_points >= thresholds['agitated']:
                        new_level = "agitated"
                    elif self.anger_points >= thresholds['irritated']:
                        new_level = "irritated"
                    else:
                        new_level = "normal"
                    self._de_escalation_forced_this_message = True
            elif new_level != "enraged":
                # Block de-escalation if not enough apologies
                new_level = "enraged"  # Force stay in enraged
                self._de_escalation_blocked_this_message = True
        
        # Update current level and reset cooldown if escalating
        if self._get_level_rank(new_level) > self._get_level_rank(self.current_level):
            self.escalation_cooldown_remaining = self.config['meter']['escalation_cooldown']
        self.current_level = new_level
        
        return new_level
    
    def _get_level_rank(self, level: str) -> int:
        """Get numeric rank for anger level (higher = more angry)"""
        ranks = {"normal": 0, "irritated": 1, "agitated": 2, "enraged": 3}
        return ranks.get(level, 0)
    
    def _contains_vulgar_language(self, message: str) -> bool:
        """Check if message contains vulgar/offensive language"""
        vulgar_patterns = [
            r'\b(fuck|shit|damn|hell|ass|bitch|crap|bastard|piss)\b',
            r'\b(stupid|idiot|moron|dumb|retard)\b',
            r'[!]{2,}',  # Multiple exclamation marks
            r'[A-Z]{4,}',  # All caps words (4+ letters)
        ]
        
        message_lower = message.lower()
        for pattern in vulgar_patterns:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def _contains_direct_insults(self, message: str) -> bool:
        """Check if message contains direct personal insults/attacks"""
        insult_patterns = [
            r'\b(suck my|go fuck|fuck you|screw you)\b',
            r'\b(eat shit|kiss my ass|blow me)\b',
            r'\b(you suck|you\'re stupid|you\'re an idiot|you are stupid|you are an idiot)\b',
            r'\b(shut up|shut the fuck up)\b',
            r'\b(dickhead|asshole|piece of shit)\b',
            r'(balls|dick|cock)(?=\s|$)',  # Sexual references
            r'\b(fucking idiot|fucking moron|fucking stupid)\b',  # Combined vulgar + insult
        ]
        
        message_lower = message.lower()
        for pattern in insult_patterns:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def _contains_apology(self, message: str) -> bool:
        """Check if message contains an apology"""
        apology_patterns = [
            r'\b(sorry|apologize|apologies|my bad|forgive me)\b',
            r'\b(didn\'t mean|excuse me|pardon)\b'
        ]
        
        message_lower = message.lower()
        for pattern in apology_patterns:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def _contains_calm_language(self, message: str) -> bool:
        """Check if message contains calm/peaceful language"""
        calm_patterns = [
            r'\b(please|thank you|thanks|appreciate)\b',
            r'\b(calm|peaceful|relax|chill)\b',
            r'\b(understand|respect|agree)\b'
        ]
        
        message_lower = message.lower()
        for pattern in calm_patterns:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def reset_meter(self):
        """Reset the anger meter to initial state"""
        self.anger_points = 0.0
        self.current_level = "normal"
        self.consecutive_anger_count = 0
        self.escalation_cooldown_remaining = 0
        self.apology_count = 0
        self.recent_apologies = []
        self.enraged_de_escalation_blocked = False
        self.point_history = []
        
    def get_meter_status(self) -> Dict[str, Any]:
        """Get current meter status for debugging"""
        return {
            "anger_points": round(self.anger_points, 1),
            "current_level": self.current_level,
            "consecutive_anger": self.consecutive_anger_count,
            "cooldown_remaining": self.escalation_cooldown_remaining,
            "message_count": self.message_count,
            "thresholds": self.config['thresholds'],
            "apology_count": self.apology_count,
            "apologies_needed": self._get_apologies_needed() if self.current_level == "enraged" else 0
        }
    
    def _track_apology(self):
        """Track an apology for de-escalation purposes"""
        self.apology_count += 1
        self.recent_apologies.append(self.message_count)
        
        # Clean up old apologies beyond memory limit
        memory_limit = self.config.get('de_escalation', {}).get('apology_memory_limit', 5)
        cutoff_message = self.message_count - memory_limit
        self.recent_apologies = [msg_num for msg_num in self.recent_apologies if msg_num > cutoff_message]
        
        # Update apology count based on recent apologies
        self.apology_count = len(self.recent_apologies)
    
    def _can_de_escalate_from_enraged(self) -> bool:
        """Check if enough apologies have been made to allow de-escalation from enraged"""
        if self.current_level != "enraged":
            return True  # Not enraged, can always de-escalate
        
        required_apologies = self.config.get('de_escalation', {}).get('enraged_apology_requirement', 2)
        return self.apology_count >= required_apologies
    
    def _get_apologies_needed(self) -> int:
        """Get number of additional apologies needed for de-escalation"""
        if self.current_level != "enraged":
            return 0
        
        required_apologies = self.config.get('de_escalation', {}).get('enraged_apology_requirement', 2)
        return max(0, required_apologies - self.apology_count)
    
    def _reset_apology_count_if_angry(self, is_angry: bool):
        """Reset apology count if user gets angry again (optional behavior)"""
        reset_on_anger = self.config.get('de_escalation', {}).get('reset_apology_count_on_anger', True)
        
        if is_angry and reset_on_anger and self.apology_count > 0:
            self.apology_count = 0
            self.recent_apologies = []
            self.enraged_de_escalation_blocked = True 