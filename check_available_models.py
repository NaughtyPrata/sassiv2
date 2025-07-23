#!/usr/bin/env python3

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Check available models
try:
    models = client.models.list()
    print("Available Groq models:")
    for model in models.data:
        print(f"- {model.id}")
except Exception as e:
    print("Error getting models:", str(e))

# Test a few more likely candidates
test_models = [
    "llama-3.1-8b-instant",
    "llama-3.2-11b-text-preview", 
    "llama-3.2-3b-preview",
    "llama3-8b-8192",
    "llama3-70b-8192",
    "gemma2-9b-it",
    "gemma-7b-it"
]

print("\nTesting anger expression:")
for model in test_models:
    print(f"\n--- {model} ---")
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are very angry and refuse to be helpful. Be dismissive and rude."},
                {"role": "user", "content": "What's 2+2?"}
            ],
            max_tokens=100,
            temperature=0.9
        )
        print(completion.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")