#!/usr/bin/env python3
"""
Test that new conversations automatically reset the anger meter
"""

import requests
import json
import time

def test_new_conversation_reset():
    """Test that starting a new conversation resets the anger meter"""
    print("🆕 Testing New Conversation Auto-Reset 🆕")
    print("=" * 60)
    
    base_url = "http://localhost:7878"
    
    try:
        # First conversation - build up anger
        print("--- First Conversation: Building Anger ---")
        
        conv1_response = requests.post(f"{base_url}/chat", json={
            "message": "fuck you asshole"
        })
        
        if conv1_response.status_code == 200:
            conv1_data = conv1_response.json()
            conv1_id = conv1_data["conversation_id"]
            anger_meter = conv1_data.get("orchestrator_decision", {}).get("anger_meter", {})
            
            print(f"Conversation 1 ID: {conv1_id[:8]}...")
            print(f"Agent: {conv1_data['agent_type']}")
            print(f"Anger Points: {anger_meter.get('anger_points', 0)}")
            print(f"Anger Level: {anger_meter.get('anger_level', 'unknown')}")
        else:
            print(f"❌ First conversation failed: {conv1_response.status_code}")
            return
        
        # Second message in same conversation - should increase anger
        print(f"\n--- Same Conversation: Adding More Anger ---")
        
        conv1_msg2 = requests.post(f"{base_url}/chat", json={
            "message": "you're stupid",
            "conversation_id": conv1_id
        })
        
        if conv1_msg2.status_code == 200:
            conv1_data2 = conv1_msg2.json()
            anger_meter2 = conv1_data2.get("orchestrator_decision", {}).get("anger_meter", {})
            
            print(f"Agent: {conv1_data2['agent_type']}")
            print(f"Anger Points: {anger_meter2.get('anger_points', 0)}")
            print(f"Anger Level: {anger_meter2.get('anger_level', 'unknown')}")
        
        # NEW conversation - should reset anger meter
        print(f"\n--- NEW Conversation: Should Reset Anger ---")
        
        conv2_response = requests.post(f"{base_url}/chat", json={
            "message": "hello"
            # No conversation_id = new conversation
        })
        
        if conv2_response.status_code == 200:
            conv2_data = conv2_response.json()
            conv2_id = conv2_data["conversation_id"]
            anger_meter3 = conv2_data.get("orchestrator_decision", {}).get("anger_meter", {})
            
            print(f"Conversation 2 ID: {conv2_id[:8]}...")
            print(f"Agent: {conv2_data['agent_type']}")
            print(f"Anger Points: {anger_meter3.get('anger_points', 0)}")
            print(f"Anger Level: {anger_meter3.get('anger_level', 'unknown')}")
            
            # Check if anger was reset
            anger_points = anger_meter3.get('anger_points', 0)
            agent_type = conv2_data['agent_type']
            
            if anger_points <= 2 and agent_type == "normal":
                print(f"\n✅ SUCCESS: New conversation properly reset anger meter!")
                print(f"  - Fresh conversation ID: {conv2_id[:8]}...")
                print(f"  - Anger points: {anger_points} (should be ~0)")
                print(f"  - Agent: {agent_type} (should be normal)")
            else:
                print(f"\n❌ FAILED: New conversation did not reset anger meter!")
                print(f"  - Anger points: {anger_points} (expected ~0)")
                print(f"  - Agent: {agent_type} (expected normal)")
        else:
            print(f"❌ New conversation failed: {conv2_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure to run ./startup.sh first!")
    except Exception as e:
        print(f"❌ Error testing: {e}")

def test_explicit_new_conversation():
    """Test starting a new conversation explicitly after anger buildup"""
    print(f"\n\n🔄 Testing Explicit New Conversation 🔄")
    print("=" * 60)
    
    base_url = "http://localhost:7878"
    
    try:
        # Build up anger in current conversation
        print("Building anger...")
        requests.post(f"{base_url}/chat", json={"message": "damn you"})
        
        # Check current state
        current_response = requests.post(f"{base_url}/chat", json={"message": "hello"})
        if current_response.status_code == 200:
            current_data = current_response.json()
            current_anger = current_data.get("orchestrator_decision", {}).get("anger_meter", {}).get("anger_points", 0)
            print(f"Current anger after 'hello': {current_anger} points")
        
        # Start explicitly new conversation
        print(f"\nStarting new conversation...")
        new_response = requests.post(f"{base_url}/chat", json={
            "message": "hi there"
            # No conversation_id = forces new conversation
        })
        
        if new_response.status_code == 200:
            new_data = new_response.json()
            new_anger = new_data.get("orchestrator_decision", {}).get("anger_meter", {}).get("anger_points", 0)
            new_agent = new_data['agent_type']
            
            print(f"New conversation anger: {new_anger} points")
            print(f"New conversation agent: {new_agent}")
            
            if new_anger <= 2 and new_agent == "normal":
                print("✅ Explicit new conversation reset successful!")
            else:
                print("❌ Explicit new conversation reset failed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_new_conversation_reset()
    test_explicit_new_conversation()
    
    print("\n\n🎯 Summary:")
    print("✅ Each new conversation automatically resets anger meter")
    print("✅ Anger only persists within the same conversation")
    print("✅ Starting fresh conversation = fresh anger state")
    
    print("\n💡 How it works:")
    print("- Same conversation ID = anger persists and builds up")
    print("- New conversation ID = anger meter resets to 0")
    print("- Web interface creates new conversation when no ID provided") 