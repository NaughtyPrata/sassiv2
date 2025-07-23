#!/usr/bin/env python3
"""
Test script for de-escalation logic requiring two apologies for enraged agents
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.anger_meter import AngerMeter
from orchestrator.orchestrator import Orchestrator
from agents.base_agent import ChatMessage

def test_apology_tracking():
    """Test that apologies are properly tracked"""
    print("📋 Testing Apology Tracking 📋")
    print("=" * 50)
    
    meter = AngerMeter()
    
    # Get to enraged state first
    angry_sentiment = {'emotion': 'anger', 'intensity': 0.8}
    agent, info = meter.process_message("fuck you asshole", angry_sentiment)
    print(f"Initial: {agent} agent, {info['anger_points']} points")
    
    # Test apologies
    apology_messages = [
        "I'm sorry",
        "I apologize for that",
        "My bad, I didn't mean it",
        "Sorry again"
    ]
    
    for i, message in enumerate(apology_messages, 1):
        apology_sentiment = {'emotion': 'neutral', 'intensity': 0.1}
        agent, info = meter.process_message(message, apology_sentiment)
        
        apology_count = info['debug']['apology_count']
        apologies_needed = info['debug']['apologies_needed']
        de_escalation_blocked = info['debug']['de_escalation_blocked']
        
        print(f"\nApology {i}: '{message}'")
        print(f"  Agent: {agent}")
        print(f"  Apology Count: {apology_count}")
        print(f"  Apologies Needed: {apologies_needed}")
        print(f"  De-escalation Blocked: {de_escalation_blocked}")
        print(f"  Points: {info['anger_points']}")
        
        if agent != "enraged":
            print(f"  ✅ DE-ESCALATED after {apology_count} apologies!")
            break

def test_de_escalation_blocking():
    """Test that enraged agents require two apologies to de-escalate"""
    print(f"\n\n🚫 Testing De-escalation Blocking 🚫")
    print("=" * 50)
    
    meter = AngerMeter()
    
    # Scenario 1: Get to enraged, try one apology
    print("--- Scenario 1: One apology (should stay enraged) ---")
    
    # Get enraged
    meter.process_message("you fucking idiot", {'emotion': 'anger', 'intensity': 0.8})
    agent, info = meter.process_message("I'm sorry", {'emotion': 'neutral', 'intensity': 0.1})
    
    print(f"After 1 apology: {agent} agent (should be enraged)")
    print(f"Apologies needed: {info['debug']['apologies_needed']}")
    
    # Scenario 2: Second apology should allow de-escalation
    print("\n--- Scenario 2: Second apology (should de-escalate) ---")
    
    agent, info = meter.process_message("I really apologize", {'emotion': 'neutral', 'intensity': 0.1})
    
    print(f"After 2 apologies: {agent} agent (should NOT be enraged)")
    print(f"Apologies needed: {info['debug']['apologies_needed']}")
    
    if agent != "enraged":
        print("✅ De-escalation successful after 2 apologies!")
    else:
        print("❌ Still enraged - de-escalation failed")

def test_anger_reset_apologies():
    """Test that getting angry again resets apology count"""
    print(f"\n\n🔄 Testing Anger Reset of Apologies 🔄")
    print("=" * 50)
    
    meter = AngerMeter()
    
    # Get enraged
    meter.process_message("you stupid fuck", {'emotion': 'anger', 'intensity': 0.8})
    
    # Make one apology
    agent, info = meter.process_message("I'm sorry", {'emotion': 'neutral', 'intensity': 0.1})
    print(f"After 1 apology: {info['debug']['apology_count']} apologies counted")
    
    # Get angry again (should reset apology count)
    agent, info = meter.process_message("but you're still an idiot", {'emotion': 'anger', 'intensity': 0.6})
    print(f"After getting angry again: {info['debug']['apology_count']} apologies counted")
    
    # Now need two apologies again
    agent, info = meter.process_message("sorry", {'emotion': 'neutral', 'intensity': 0.1})
    print(f"After new apology: {agent} agent, {info['debug']['apology_count']} apologies, need {info['debug']['apologies_needed']} more")

async def test_full_conversation_de_escalation():
    """Test de-escalation in a full conversation with orchestrator"""
    print(f"\n\n💬 Testing Full Conversation De-escalation 💬")
    print("=" * 50)
    
    orchestrator = Orchestrator()
    conversation_history = []
    
    # Conversation that escalates then de-escalates
    conversation = [
        ("fuck you", "Get angry"),
        ("you're an asshole", "Stay angry"), 
        ("I'm sorry", "First apology - should stay enraged"),
        ("I really apologize for being rude", "Second apology - should de-escalate"),
        ("How are you doing?", "Normal conversation after de-escalation")
    ]
    
    for i, (message, description) in enumerate(conversation, 1):
        print(f"\nMessage {i}: '{message}' ({description})")
        
        # Add to conversation history
        user_message = ChatMessage(role="user", content=message)
        conversation_history.append(user_message)
        
        # Process message
        response, agent_type, analysis_data = await orchestrator.process_message(
            message, conversation_history
        )
        
        # Extract anger meter info
        anger_meter = analysis_data.get("orchestrator_decision", {}).get("anger_meter", {})
        debug_info = anger_meter.get("debug", {})
        
        print(f"  Agent: {agent_type}")
        print(f"  Points: {anger_meter.get('anger_points', 0)}")
        print(f"  Apology Count: {debug_info.get('apology_count', 0)}")
        print(f"  Apologies Needed: {debug_info.get('apologies_needed', 0)}")
        
        if "de_escalation_blocked" in anger_meter.get('change_reasons', []):
            print("  🚫 De-escalation blocked - need more apologies")
        
        # Add assistant response to history
        assistant_message = ChatMessage(role="assistant", content=response)
        conversation_history.append(assistant_message)

if __name__ == "__main__":
    async def main():
        test_apology_tracking()
        test_de_escalation_blocking()
        test_anger_reset_apologies()
        await test_full_conversation_de_escalation()
        
        print("\n\n✅ De-escalation Testing Complete!")
        print("🔧 Configuration: Requires 2 apologies to de-escalate from enraged")
        print("📝 Edit anger_config.yaml to change apology requirements")
    
    asyncio.run(main()) 