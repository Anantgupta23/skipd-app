"""
Gemini Client Helper Module
Integrates the official Google Gen AI SDK (google-genai) with python-dotenv.
Default Model: gemini-3.5-flash-lite (with seamless fallback support)
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEFAULT_MODEL = "gemini-3.5-flash-lite"
FALLBACK_MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError, ClientError, ServerError
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    APIError = Exception
    ClientError = Exception
    ServerError = Exception
    types = None

_cached_client = None
_cached_key = None

def get_gemini_client(api_key: Optional[str] = None) -> "genai.Client":
    """
    Initializes and returns the official Google Gen AI Client.
    Caches the client instance to maintain persistent chat session connections.
    """
    global _cached_client, _cached_key

    if not GENAI_AVAILABLE:
        raise ImportError(
            "The official Google Gen AI SDK is not installed. "
            "Please run: pip install google-genai python-dotenv"
        )

    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key or key.strip() == "" or key.strip() == "your_key_here":
        raise ValueError(
            "Missing GEMINI_API_KEY. Please ensure GEMINI_API_KEY is set in your .env file "
            "or passed directly to the function."
        )

    clean_key = key.strip()
    if _cached_client is None or _cached_key != clean_key:
        _cached_client = genai.Client(api_key=clean_key)
        _cached_key = clean_key

    return _cached_client

def generate_text(prompt: str, model: str = DEFAULT_MODEL, system_instruction: Optional[str] = None, api_key: Optional[str] = None) -> str:
    """
    Sends a single-turn prompt to Gemini and returns the generated output text.

    Args:
        prompt: The text prompt to send to Gemini.
        model: The Gemini model name (defaults to 'gemini-3.5-flash-lite').
        system_instruction: Optional system persona instructions.
        api_key: Optional API key override. If not provided, loads from .env.

    Returns:
        The generated text content string.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    client = get_gemini_client(api_key=api_key)

    config = None
    if system_instruction and types:
        config = types.GenerateContentConfig(system_instruction=system_instruction)

    models_to_try = [model]
    for m in FALLBACK_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    last_error = None
    for target_model in models_to_try:
        try:
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=config
            )
            if hasattr(response, "text") and response.text:
                return response.text
            return ""
        except (ClientError, ServerError, APIError) as e:
            err_msg = str(e)
            last_error = e
            if "no longer available" in err_msg or "503" in err_msg or "NOT_FOUND" in err_msg:
                continue
            raise RuntimeError(f"Google Gen AI API Error: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Error during Gemini text generation: {e}") from e

    raise RuntimeError(f"All model attempts failed. Last error: {last_error}")

def start_chat(model: str = DEFAULT_MODEL, system_instruction: Optional[str] = None, api_key: Optional[str] = None):
    """
    Creates and returns a persistent multi-turn chat session with Gemini.

    Args:
        model: The Gemini model name (defaults to 'gemini-3.5-flash-lite').
        system_instruction: Optional system instruction (e.g. brand persona & rules).
        api_key: Optional API key override. If not provided, loads from .env.

    Returns:
        A Chat instance capable of sending messages with history retention:
        chat.send_message("...")
    """
    client = get_gemini_client(api_key=api_key)

    config = None
    if system_instruction and types:
        config = types.GenerateContentConfig(system_instruction=system_instruction)

    models_to_try = [model]
    for m in FALLBACK_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    last_error = None
    for target_model in models_to_try:
        try:
            chat = client.chats.create(model=target_model, config=config)
            chat._client_ref = client
            return chat
        except (ClientError, ServerError, APIError) as e:
            last_error = e
            continue
        except Exception as e:
            raise RuntimeError(f"Error initializing Gemini chat session: {e}") from e

    raise RuntimeError(f"Failed to start Gemini chat session: {last_error}")

if __name__ == "__main__":
    print(f"Gemini Client Module ready with default model '{DEFAULT_MODEL}'.")
