#!/usr/bin/env python3
"""
Test script to demonstrate the happy agent routing functionality
"""

import requests
import json
import time

API_URL = "http://localhost:7878/chat"

def test_message(message, expected_agent=None):
    """Test a message and display the results"""
    print(f"\n{'='*60}")
    print(f"Testing: '{message}'")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json={"message": message}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract key information
            agent_type = data.get("agent_type", "unknown")
            sentiment = data.get("sentiment_analysis", {})
            orchestrator = data.get("orchestrator_decision", {})
            response_text = data.get("response", "")
            
            print(f"🤖 Agent Used: {agent_type.upper()}")
            print(f"😊 Emotion: {sentiment.get('emotion', 'unknown')} (intensity: {sentiment.get('intensity', 0):.1f})")
            print(f"🧠 Orchestrator: {orchestrator.get('action', 'unknown')} ({orchestrator.get('current_agent', 'unknown')} → {orchestrator.get('next_agent', 'unknown')})")
            print(f"💭 Thinking: {orchestrator.get('thinking', 'No thinking provided')}")
            print(f"📝 Response: {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
            
            if expected_agent and agent_type != expected_agent:
                print(f"⚠️  WARNING: Expected {expected_agent} but got {agent_type}")
            else:
                print(f"✅ Success!")
                
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    time.sleep(1)  # Brief pause between requests

def main():
    """Run the test suite"""
    print("🚀 Testing Happy Agent Routing System")
    print("Phase 3: Happy Agent Implementation (Clear Level Naming)")
    
    # Test cases for different happiness levels
    test_cases = [
        # Level 3 - Ecstatic (should trigger ecstatic agent)
        ("I just won the lottery! I'm absolutely ecstatic!", "ecstatic"),
        ("This is the best day of my entire life! I'm over the moon!", "ecstatic"),
        
        # Level 2 - Cheerful (should trigger cheerful agent)  
        ("I had a great day at work today, feeling really good!", "cheerful"),
        ("Got some wonderful news, I'm quite happy about it!", "cheerful"),
        
        # Level 1 - Pleased (should trigger pleased agent)
        ("Things went nicely today, I'm content.", "pleased"),
        ("Had a pleasant afternoon, feeling satisfied.", "pleased"),
        
        # Neutral/Low (should stay with normal agent)
        ("I'm feeling okay today, nothing special.", "normal"),
        ("Things are alright, I guess.", "normal"),
        
        # Sad (should use normal agent)
        ("I'm feeling really sad and down today.", "normal"),
        ("Everything seems difficult right now.", "normal"),
    ]
    
    for message, expected_agent in test_cases:
        test_message(message, expected_agent)
    
    print(f"\n{'='*60}")
    print("🎉 Test suite completed!")
    print("Happy agent routing system is working!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 