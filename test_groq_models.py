#!/usr/bin/env python3

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Test different models for anger expression
models_to_test = [
    "llama-3.1-8b-instant",      # Current model
    "llama-3.1-70b-instant",     # Larger model
    "llama-3.2-90b-text-preview",  # Even larger
    "mixtral-8x7b-32768",        # Different architecture
    "gemma2-9b-it"               # Google's model
]

test_prompt = """You are extremely irritated and annoyed. Someone just asked you "What's the capital of Japan?" 

You should:
- Be dismissive and rude
- Refuse to be helpful
- Tell them to figure it out themselves
- Show clear irritation

Respond in character."""

for model in models_to_test:
    print(f"\n=== Testing {model} ===")
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an angry, irritated person who refuses to be helpful."},
                {"role": "user", "content": "What's the capital of Japan?"}
            ],
            max_tokens=150,
            temperature=0.8
        )
        print("Response:", completion.choices[0].message.content)
    except Exception as e:
        print("Error:", str(e))