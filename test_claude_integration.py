#!/usr/bin/env python3
"""
Test script demonstrating Claude Code integration with the emotional chatbot API

This script shows how Claude Code can interact with your emotional chatbot system
for testing, debugging, and development purposes.
"""

from claude_integration import EmotionalChatbotClient, quick_chat, test_emotional_escalation
import time


def main():
    print("🚀 Claude Code Integration Test")
    print("=" * 50)
    
    # Initialize client
    client = EmotionalChatbotClient()
    
    # 1. Health check
    print("\n1️⃣ Health Check")
    health = client.health_check()
    if "error" in health:
        print(f"❌ Server not available: {health['error']}")
        print("💡 Make sure to run: ./startup.sh")
        return
    
    print(f"✅ Server healthy at {client.base_url}")
    
    # 2. Reset state for clean test
    print("\n2️⃣ Resetting State")
    reset_result = client.reset_state()
    print(f"🔄 State reset: {reset_result.get('message', 'Done')}")
    
    # 3. Test basic conversation
    print("\n3️⃣ Basic Conversation Test")
    messages = [
        "Hi there! I'm Claude Code testing your system.",
        "How does the emotional analysis work?",
        "That's really interesting!"
    ]
    
    for msg in messages:
        print(f"\n👤 User: {msg}")
        response = client.chat(msg)
        print(client.format_response(response))
        time.sleep(1)  # Brief pause between messages
    
    # 4. Test emotional escalation
    print("\n4️⃣ Emotional Escalation Test")
    print("Testing anger escalation sequence...")
    
    # Start new conversation for escalation test
    client.start_new_conversation()
    
    escalation_messages = [
        "I need help with something",
        "This isn't working properly",
        "I'm getting really frustrated here",
        "This is absolutely ridiculous!",
        "I can't stand this anymore!"
    ]
    
    for i, msg in enumerate(escalation_messages, 1):
        print(f"\n📈 Escalation Step {i}")
        print(f"👤 User: {msg}")
        response = client.chat(msg)
        
        # Extract key info for escalation tracking
        agent_type = response.get("agent_type", "unknown")
        insights = response.get("orchestrator_insights", {})
        anger_points = insights.get("anger_points", "N/A")
        
        print(f"🤖 Agent: {agent_type}")
        print(f"😤 Anger Points: {anger_points}")
        print(f"💬 Response: {response.get('response', '')[:100]}...")
        
        time.sleep(1)
    
    # 5. Test conversation history
    print("\n5️⃣ Conversation History")
    history = client.get_conversation_history()
    if "error" not in history:
        message_count = len(history.get("messages", []))
        print(f"📚 Retrieved {message_count} messages from conversation history")
    else:
        print(f"❌ Error getting history: {history['error']}")
    
    # 6. Test quick chat function
    print("\n6️⃣ Quick Chat Function Test")
    quick_response = quick_chat("Testing the quick chat function!")
    print("Quick chat result:")
    print(quick_response)
    
    print("\n✅ Integration test complete!")
    print("\n🔧 Available functions for Claude Code:")
    print("- EmotionalChatbotClient() - Full featured client")
    print("- quick_chat(message) - Simple one-off messages")  
    print("- test_emotional_escalation() - Predefined escalation test")


def demo_claude_usage():
    """Demonstrate how Claude Code would use the integration"""
    print("\n" + "="*50)
    print("🧠 Claude Code Usage Demo")
    print("="*50)
    
    print("\n📋 How Claude Code can use this integration:")
    
    # Example 1: Quick testing
    print("\n1. Quick testing:")
    print(">>> quick_chat('Test message')")
    result = quick_chat("Hello from Claude Code demo!")
    print(result)
    
    # Example 2: Full client usage
    print("\n2. Full client for complex testing:")
    client = EmotionalChatbotClient()
    client.reset_state()
    
    print(">>> client = EmotionalChatbotClient()")
    print(">>> client.reset_state()")
    print(">>> response = client.chat('Testing anger escalation')")
    
    response = client.chat("I'm really angry about this service!")
    insights = response.get("orchestrator_insights", {})
    print(f"Agent type: {response.get('agent_type')}")
    print(f"Anger points: {insights.get('anger_points', 'N/A')}")
    
    # Example 3: Emotional progression analysis
    print("\n3. Emotional progression analysis:")
    print(">>> test_emotional_escalation()")
    print("(Running abbreviated version...)")
    
    brief_test = [
        "Hello there",
        "I'm getting frustrated", 
        "This is making me angry!"
    ]
    
    client.start_new_conversation()
    results = client.analyze_emotional_progression(brief_test)
    
    for result in results:
        if "error" not in result:
            print(f"Step {result['message_number']}: {result['agent_type']} agent")


if __name__ == "__main__":
    main()
    demo_claude_usage()