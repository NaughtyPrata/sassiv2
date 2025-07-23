"""
Claude Code Integration Client for Emotional Chatbot API

This module provides a simple API client that Claude Code can use to interact
with the emotional chatbot system for testing and development purposes.
"""

import requests
import json
from typing import Optional, Dict, Any, List
from datetime import datetime


class EmotionalChatbotClient:
    """Client for interacting with the emotional chatbot API"""
    
    def __init__(self, base_url: str = "http://localhost:7878"):
        self.base_url = base_url.rstrip('/')
        self.conversation_id: Optional[str] = None
        
    def chat(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a message to the chatbot and get response with full analysis data
        
        Args:
            message: The message to send
            conversation_id: Optional conversation ID (uses current if not provided)
            
        Returns:
            Dictionary containing response, agent_type, sentiment analysis, etc.
        """
        url = f"{self.base_url}/chat"
        payload = {
            "message": message,
            "conversation_id": conversation_id or self.conversation_id
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            # Store conversation ID for future messages
            self.conversation_id = data.get("conversation_id")
            
            return data
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_conversation_history(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get the full conversation history"""
        conv_id = conversation_id or self.conversation_id
        if not conv_id:
            return {"error": "No conversation ID available"}
            
        url = f"{self.base_url}/conversations/{conv_id}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def reset_state(self) -> Dict[str, Any]:
        """Reset the orchestrator state and clear all conversations"""
        url = f"{self.base_url}/reset"
        
        try:
            response = requests.post(url, timeout=10)
            response.raise_for_status()
            
            # Clear local conversation ID since state is reset
            self.conversation_id = None
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the API server is running"""
        url = f"{self.base_url}/health"
        
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Health check failed: {str(e)}"}
    
    def start_new_conversation(self) -> str:
        """Start a new conversation by clearing the current conversation ID"""
        self.conversation_id = None
        return "New conversation started - next message will create new conversation ID"
    
    def analyze_emotional_progression(self, messages: List[str]) -> List[Dict[str, Any]]:
        """
        Send a series of messages and analyze the emotional progression
        Useful for testing how the system responds to escalating scenarios
        """
        results = []
        
        for i, message in enumerate(messages):
            print(f"Sending message {i+1}/{len(messages)}: {message[:50]}...")
            
            result = self.chat(message)
            if "error" not in result:
                analysis = {
                    "message_number": i + 1,
                    "user_message": message,
                    "agent_response": result.get("response", ""),
                    "agent_type": result.get("agent_type", ""),
                    "sentiment": result.get("sentiment_analysis", {}),
                    "orchestrator_insights": result.get("orchestrator_insights", {})
                }
                results.append(analysis)
            else:
                results.append({"message_number": i + 1, "error": result["error"]})
        
        return results
    
    def format_response(self, response_data: Dict[str, Any]) -> str:
        """Format API response for readable display"""
        if "error" in response_data:
            return f"❌ Error: {response_data['error']}"
        
        agent_type = response_data.get("agent_type", "unknown")
        response_text = response_data.get("response", "")
        
        # Extract key insights
        insights = response_data.get("orchestrator_insights", {})
        anger_points = insights.get("anger_points", "N/A")
        
        formatted = f"""
🤖 Agent: {agent_type}
💬 Response: {response_text}
😤 Anger Points: {anger_points}
🔍 Conversation ID: {response_data.get("conversation_id", "N/A")[:8]}...
        """.strip()
        
        return formatted


# Convenience functions for Claude Code to use directly
def quick_chat(message: str, base_url: str = "http://localhost:7878") -> str:
    """Quick chat function for single messages"""
    client = EmotionalChatbotClient(base_url)
    response = client.chat(message)
    return client.format_response(response)


def test_emotional_escalation(base_url: str = "http://localhost:7878") -> List[Dict[str, Any]]:
    """Test emotional escalation with a predefined sequence"""
    client = EmotionalChatbotClient(base_url)
    
    # Reset state first
    client.reset_state()
    
    test_messages = [
        "Hello, how are you today?",
        "I'm having some issues with my order",
        "This is really frustrating, nothing is working!",
        "I can't believe this! Your service is terrible!",
        "I DEMAND TO SPEAK TO A MANAGER RIGHT NOW!"
    ]
    
    return client.analyze_emotional_progression(test_messages)


if __name__ == "__main__":
    # Demo usage
    print("🔧 Testing Emotional Chatbot API Client")
    
    client = EmotionalChatbotClient()
    
    # Health check
    health = client.health_check()
    if "error" in health:
        print(f"❌ Server not available: {health['error']}")
        exit(1)
    
    print("✅ Server is healthy")
    
    # Test conversation
    print("\n📝 Testing conversation...")
    response = client.chat("Hello! I'm testing the integration.")
    print(client.format_response(response))