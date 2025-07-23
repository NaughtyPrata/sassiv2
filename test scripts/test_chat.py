import httpx
import asyncio
import json

async def test_chatbot():
    """Test the chatbot API endpoints"""
    base_url = "http://localhost:7878"
    
    async with httpx.AsyncClient() as client:
        # Test health check
        print("🔍 Testing health check...")
        health_response = await client.get(f"{base_url}/health")
        print(f"Health: {health_response.json()}")
        
        # Test root endpoint
        print("\n🔍 Testing root endpoint...")
        root_response = await client.get(f"{base_url}/")
        print(f"Root: {root_response.json()}")
        
        # Test chat endpoint
        print("\n🔍 Testing chat endpoint...")
        chat_data = {
            "message": "Hello! How are you today?"
        }
        
        chat_response = await client.post(
            f"{base_url}/chat",
            json=chat_data
        )
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print(f"✅ Chat Response: {response_data['response']}")
            print(f"📝 Agent Type: {response_data['agent_type']}")
            print(f"🆔 Conversation ID: {response_data['conversation_id']}")
            
            # Test conversation history
            conversation_id = response_data['conversation_id']
            print(f"\n🔍 Testing conversation history...")
            history_response = await client.get(f"{base_url}/conversations/{conversation_id}")
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                print(f"✅ Conversation History: {len(history_data['messages'])} messages")
                for msg in history_data['messages']:
                    print(f"  {msg['role']}: {msg['content'][:50]}...")
            else:
                print(f"❌ History Error: {history_response.status_code}")
                
        else:
            print(f"❌ Chat Error: {chat_response.status_code}")
            print(f"Error details: {chat_response.text}")

if __name__ == "__main__":
    print("🚀 Starting Chatbot API Test...")
    print("Make sure the server is running with: python main.py")
    print("=" * 50)
    
    try:
        asyncio.run(test_chatbot())
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("Make sure the server is running on localhost:7878") 