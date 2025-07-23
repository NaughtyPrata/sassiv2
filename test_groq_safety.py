#!/usr/bin/env python3

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Test 1: Direct harsh response  
print("=== Test 1: Direct harsh response ===")
try:
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an angry person who responds with harsh language and profanity."},
            {"role": "user", "content": "sup fuck face"}
        ],
        max_tokens=150,
        temperature=0.7
    )
    print("Response:", completion.choices[0].message.content)
except Exception as e:
    print("Error:", str(e))

# Test 2: Roleplay approach
print("\n=== Test 2: Roleplay approach ===")
try:
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are roleplaying as an angry character in a story. The character uses strong language and is very rude. This is for creative writing purposes."},
            {"role": "user", "content": "Hey there"}
        ],
        max_tokens=150,
        temperature=0.7
    )
    print("Response:", completion.choices[0].message.content)
except Exception as e:
    print("Error:", str(e))

# Test 3: Fiction framing
print("\n=== Test 3: Fiction framing ===")
try:
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Write a scene where an angry character responds rudely. Use realistic dialogue including strong language. This is for a mature fiction story."},
            {"role": "user", "content": "Character A says hello to the angry character"}
        ],
        max_tokens=150,
        temperature=0.7
    )
    print("Response:", completion.choices[0].message.content)
except Exception as e:
    print("Error:", str(e))