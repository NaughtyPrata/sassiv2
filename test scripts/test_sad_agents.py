#!/usr/bin/env python3
"""
Test script for sad agents functionality
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator.orchestrator import Orchestrator
from agents.base_agent import ChatMessage

async def test_sad_agents():
    """Test sad agents with different sadness levels"""
    
    print("🧪 Testing Sad Agents Implementation")
    print("=" * 50)
    
    orchestrator = Orchestrator()
    
    # Test messages with different sadness levels
    test_cases = [
        {
            "message": "I'm feeling a bit down today, everything seems gray and melancholy.",
            "expected_agent": "melancholy",
            "description": "Mild sadness - should trigger melancholy agent"
        },
        {
            "message": "I'm really struggling with deep sadness and sorrow. My heart feels so heavy.",
            "expected_agent": "sorrowful", 
            "description": "Moderate sadness - should trigger sorrowful agent"
        },
        {
            "message": "I'm drowning in depression and despair. Everything feels hopeless and overwhelming.",
            "expected_agent": "depressed",
            "description": "Intense sadness - should trigger depressed agent"
        },
        {
            "message": "I feel a little nostalgic and wistful about the past.",
            "expected_agent": "melancholy",
            "description": "Gentle sadness - should trigger melancholy agent"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_case['description']}")
        print(f"📝 Message: \"{test_case['message']}\"")
        
        # Create conversation history
        conversation_history = [
            ChatMessage(role="user", content=test_case["message"])
        ]
        
        try:
            # Process message through orchestrator
            response, agent_type, analysis_data = await orchestrator.process_message(
                test_case["message"], 
                conversation_history
            )
            
            # Extract analysis data
            sentiment = analysis_data.get("sentiment_analysis", {})
            orchestrator_decision = analysis_data.get("orchestrator_decision", {})
            
            print(f"🎭 Selected Agent: {agent_type}")
            print(f"😢 Detected Emotion: {sentiment.get('emotion', 'unknown')}")
            print(f"📊 Intensity: {sentiment.get('intensity', 0):.2f}")
            print(f"🧠 Orchestrator Thinking: {orchestrator_decision.get('thinking', 'N/A')}")
            print(f"💬 Response Preview: {response[:100]}...")
            
            # Check if correct agent was selected
            if agent_type == test_case["expected_agent"]:
                print("✅ PASS: Correct agent selected")
            else:
                print(f"❌ FAIL: Expected {test_case['expected_agent']}, got {agent_type}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 Sad Agents Test Complete")

if __name__ == "__main__":
    asyncio.run(test_sad_agents()) 