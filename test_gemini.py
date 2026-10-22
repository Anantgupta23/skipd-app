"""
Verification Test Script for Gemini API Client
Tests generate_text and start_chat with prompt 'Hello Gemini'.
"""

import sys
from gemini_client import generate_text, start_chat, DEFAULT_MODEL

def main():
    print(f">> Testing Gemini API Integration with model: {DEFAULT_MODEL}")
    prompt = "Hello Gemini! Give a short 1-line friendly greeting."

    # Test 1: Single-turn text generation
    print(f"\n[Test 1] Single-turn prompt: '{prompt}'")
    try:
        response_text = generate_text(prompt)
        print("Success! Gemini response:")
        print("-" * 50)
        print(response_text.strip())
        print("-" * 50)
    except Exception as e:
        print(f"Error during Test 1: {e}")
        sys.exit(1)

    # Test 2: Multi-turn chat session
    print("\n[Test 2] Multi-turn Chat Session:")
    try:
        chat = start_chat()
        reply1 = chat.send_message("My name is SKIPD.")
        print(f"User: My name is SKIPD.")
        print(f"Gemini: {reply1.text.strip()}")

        reply2 = chat.send_message("What is my name?")
        print(f"User: What is my name?")
        print(f"Gemini: {reply2.text.strip()}")
        print("-" * 50)
        print("Multi-turn chat memory verified successfully!")
    except Exception as e:
        print(f"Error during Test 2: {e}")
        sys.exit(1)

    print("\n All Gemini API verification checks passed successfully!")

if __name__ == "__main__":
    main()
