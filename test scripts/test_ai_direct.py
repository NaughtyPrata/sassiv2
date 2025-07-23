import asyncio
from groq import Groq
import os
import json
import re

async def test_deepseek_direct():
    """Test DeepSeek R1 model directly"""
    
    print("🧠 Testing DeepSeek R1 Model Direct Access")
    print("=" * 50)
    
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Test simple reasoning
        response = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{
                "role": "user", 
                "content": """Analyze this emotional scenario and respond with JSON:

User says: "I'm really frustrated with this service!"
Current agent: normal
Emotion: frustration, intensity: 0.7

Available agents: normal, irritated, agitated, enraged, pleased, cheerful, ecstatic

Respond with JSON:
{
    "next_agent": "best_agent_choice",
    "action": "escalate|de-escalate|maintain", 
    "thinking": "your reasoning",
    "confidence": 0.8
}"""
            }],
            temperature=0.6,
            max_tokens=1000  # More tokens for reasoning
        )
        
        print("✅ DeepSeek R1 Full Response:")
        content = response.choices[0].message.content
        print(content)
        print("\n" + "="*50)
        
        # Test JSON parsing with reasoning handling
        if '</think>' in content:
            # Extract content after thinking section
            post_think = content.split('</think>')[-1].strip()
            json_match = re.search(r'\{.*\}', post_think, re.DOTALL)
            print("📝 Found reasoning section, extracting JSON from post-think content")
        else:
            # Look for JSON in the entire response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            print("📝 No reasoning section found, extracting JSON from full content")
            
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                print("✅ Successfully Parsed JSON:")
                for key, value in parsed.items():
                    print(f"  {key}: {value}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Raw JSON: {json_match.group()}")
        else:
            print("❌ No JSON found in response")
            
    except Exception as e:
        print(f"❌ Error testing DeepSeek R1: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    asyncio.run(test_deepseek_direct()) 