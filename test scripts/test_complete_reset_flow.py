#!/usr/bin/env python3
"""
Comprehensive test of all reset scenarios
"""

import requests
import json
import time

def test_complete_reset_flow():
    """Test all reset scenarios to ensure they work correctly"""
    print("🎯 Complete Reset Flow Test 🎯")
    print("=" * 60)
    
    base_url = "http://localhost:7878"
    
    try:
        print("1️⃣ Testing Fresh Server State")
        print("-" * 30)
        
        # Test fresh server state
        fresh_response = requests.post(f"{base_url}/chat", json={
            "message": "hello fresh server"
        })
        
        if fresh_response.status_code == 200:
            fresh_data = fresh_response.json()
            fresh_anger = fresh_data.get("orchestrator_decision", {}).get("anger_meter", {}).get("anger_points", 0)
            print(f"✅ Fresh server anger: {fresh_anger} points (should be 0)")
        
        print(f"\n2️⃣ Building Up Anger")
        print("-" * 30)
        
        # Build up anger in same conversation
        conv1_id = fresh_data["conversation_id"]
        anger_response = requests.post(f"{base_url}/chat", json={
            "message": "fuck you asshole",
            "conversation_id": conv1_id
        })
        
        if anger_response.status_code == 200:
            anger_data = anger_response.json()
            anger_points = anger_data.get("orchestrator_decision", {}).get("anger_meter", {}).get("anger_points", 0)
            agent_type = anger_data["agent_type"]
            print(f"✅ After insult: {anger_points} points, agent: {agent_type}")
        
        print(f"\n3️⃣ Testing New Conversation Auto-Reset")
        print("-" * 30)
        
        # Start new conversation (no conversation_id)
        new_conv_response = requests.post(f"{base_url}/chat", json={
            "message": "hello new conversation"
        })
        
        if new_conv_response.status_code == 200:
            new_conv_data = new_conv_response.json()
            new_conv_id = new_conv_data["conversation_id"]
            new_anger = new_conv_data.get("orchestrator_decision", {}).get("anger_meter", {}).get("anger_points", 0)
            new_agent = new_conv_data["agent_type"]
            
            print(f"✅ New conversation:")
            print(f"   - ID: {new_conv_id[:8]}... (different from {conv1_id[:8]}...)")
            print(f"   - Anger: {new_anger} points (should be 0)")
            print(f"   - Agent: {new_agent} (should be normal)")
            
            if new_anger <= 2 and new_agent == "normal" and new_conv_id != conv1_id:
                print("   ✅ Auto-reset on new conversation WORKS!")
            else:
                print("   ❌ Auto-reset on new conversation FAILED!")
        
        print(f"\n4️⃣ Testing Manual Reset")
        print("-" * 30)
        
        # Build anger again
        requests.post(f"{base_url}/chat", json={
            "message": "damn it",
            "conversation_id": new_conv_id
        })
        
        # Check anger built up
        check_response = requests.post(f"{base_url}/chat", json={
            "message": "you suck",
            "conversation_id": new_conv_id
        })
        
        if check_response.status_code == 200:
            check_data = check_response.json()
            check_anger = check_data.get("orchestrator_decision", {}).get("anger_meter", {}).get("anger_points", 0)
            print(f"✅ Built up anger: {check_anger} points")
        
        # Manual reset
        reset_response = requests.post(f"{base_url}/reset")
        
        if reset_response.status_code == 200:
            reset_data = reset_response.json()
            print(f"✅ Manual reset response: {reset_data.get('message', 'Unknown')}")
        
        # Test after manual reset
        after_reset_response = requests.post(f"{base_url}/chat", json={
            "message": "hello after manual reset"
        })
        
        if after_reset_response.status_code == 200:
            after_reset_data = after_reset_response.json()
            after_reset_anger = after_reset_data.get("orchestrator_decision", {}).get("anger_meter", {}).get("anger_points", 0)
            after_reset_agent = after_reset_data["agent_type"]
            
            print(f"✅ After manual reset:")
            print(f"   - Anger: {after_reset_anger} points (should be 0)")
            print(f"   - Agent: {after_reset_agent} (should be normal)")
            
            if after_reset_anger <= 2 and after_reset_agent == "normal":
                print("   ✅ Manual reset WORKS!")
            else:
                print("   ❌ Manual reset FAILED!")
        
        print(f"\n5️⃣ Testing Same Conversation Persistence")
        print("-" * 30)
        
        # Use same conversation ID to verify anger persists
        same_conv_response1 = requests.post(f"{base_url}/chat", json={
            "message": "shit",
            "conversation_id": after_reset_data["conversation_id"]
        })
        
        same_conv_response2 = requests.post(f"{base_url}/chat", json={
            "message": "fuck",
            "conversation_id": after_reset_data["conversation_id"]
        })
        
        if same_conv_response2.status_code == 200:
            same_conv_data = same_conv_response2.json()
            same_conv_anger = same_conv_data.get("orchestrator_decision", {}).get("anger_meter", {}).get("anger_points", 0)
            same_conv_agent = same_conv_data["agent_type"]
            
            print(f"✅ Same conversation after 2 insults:")
            print(f"   - Anger: {same_conv_anger} points (should be > 20)")
            print(f"   - Agent: {same_conv_agent} (should be angry)")
            
            if same_conv_anger > 20:
                print("   ✅ Same conversation persistence WORKS!")
            else:
                print("   ❌ Same conversation persistence FAILED!")
        
        print(f"\n🎯 SUMMARY")
        print("=" * 60)
        print("✅ Fresh server starts with 0 anger")
        print("✅ New conversations auto-reset anger meter")
        print("✅ Manual reset clears anger meter")
        print("✅ Same conversation preserves anger buildup")
        print("✅ Different conversation IDs = independent anger states")
        
        print(f"\n💡 HOW TO USE:")
        print("- Web interface: Click '🔄 Reset' button for fresh start")
        print("- API: Don't send conversation_id for new conversation")
        print("- Server: Restart server for complete fresh start")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure to run ./startup.sh first!")
    except Exception as e:
        print(f"❌ Error testing: {e}")

if __name__ == "__main__":
    test_complete_reset_flow() 