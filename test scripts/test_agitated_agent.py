#!/usr/bin/env python3
"""
Test script for the updated sarcastic agitated agent
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.angry_level2_agitated_agent import AngryLevel2AgitatedAgent
from agents.base_agent import ChatMessage

async def test_agitated_agent():
    """Test the agitated agent directly with sarcastic responses"""
    
    print("🧪 Testing Sarcastic Agitated Agent")
    print("=" * 50)
    
    agitated_agent = AngryLevel2AgitatedAgent()
    
    # Test messages
    test_messages = [
        "How are you doing today?",
        "Can you help me with something?", 
        "You seem upset about something",
        "Why are you being difficult?",
        "I think you could be more helpful"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔍 Test {i}: \"{message}\"")
        
        # Create conversation history
        conversation_history = [
            ChatMessage(role="user", content=message)
        ]
        
        try:
            # Generate response directly from agitated agent
            response = await agitated_agent.generate_response(conversation_history)
            
            print(f"💬 Response: {response}")
            
            # Check for sarcastic elements
            has_double_punctuation = "??" in response or "!!" in response
            has_sarcasm_words = any(word in response.upper() for word in ["OH", "REALLY", "SURE", "FANTASTIC", "WONDERFUL"])
            has_thinking_tag = "<t>" in response and "</t>" in response
            
            print(f"✅ Has thinking tag: {has_thinking_tag}")
            print(f"✅ Has double punctuation: {has_double_punctuation}")
            print(f"✅ Has sarcastic words: {has_sarcasm_words}")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 Agitated Agent Test Complete")

if __name__ == "__main__":
    asyncio.run(test_agitated_agent()) 