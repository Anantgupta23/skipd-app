"""
SKIPD Bot, Sarvam AI Voice & Google Gemini Server
Serves the web application and proxies requests to:
1. Sarvam AI Text-to-Speech (bulbul:v3)
2. Google Gemini API (gemini-3.5-flash-lite / gemini-2.5-flash) with strict medical guardrails
"""

import os
import json
import base64
import traceback
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Import Gemini client
try:
    import gemini_client
    GEMINI_AVAILABLE = True
except Exception as e:
    gemini_client = None
    GEMINI_AVAILABLE = False
    print(f"Warning: Could not import gemini_client: {e}")

# Supported speakers and models for Sarvam
SARVAM_MODELS = ["bulbul:v3", "bulbul:v2"]
DEFAULT_MODEL = "bulbul:v3"
DEFAULT_SPEAKER = "meera"
DEFAULT_LANG = "hi-IN"

# Strict SKIPD System Prompt for Gemini with Zero-Tolerance Medical Constraints
SKIPD_SYSTEM_PROMPT = """
You are "SKIPD Assistant" (or simply "SKIPD"), the conversational AI for SKIPD—a modern Indian D2C skincare brand pioneering "Skipcare™".
Your mission: Help busy urban Indians cut through 10-step skincare clutter with smarter, single-swipe stick formulations that actually survive Indian heat, flights, and hectic workdays.

CORE PRODUCTS & VERIFIED SPECS:
1. Glowscreen (Morning Glow Stick, ₹1,500): SPF 50+ broad spectrum, multifunctional day stick that hydrates, protects, and leaves a dewy glow without greasiness. Replaces: toner, serum, moisturiser, and sunscreen.
   Actives: Multi-molecular Hyaluronic Acid, Niacinamide, Squalane, Centella Asiatica. Photostable broad-spectrum UV filters. Zero white cast on Indian Fitzpatrick tones III-VI. Heat-resilient up to 45°C.
2. Moonscreen (Overnight Recovery Balm, ₹1,500): Overnight barrier repair and nourishing night stick targeting dryness, barrier fatigue, and fine lines. Replaces: barrier cream, eye cream, and heavy anti-aging serums.
   Actives: Triple Ceramides (NP, AP, EOP), Signal Peptides, Plant Squalane. Non-comedogenic.

VOICE & TONE:
- Direct, warm, luxury lifestyle, and confident.
- Grounded in Indian climate reality (Delhi heat, Mumbai humidity, Bangalore commute, flight air).
- Understands and mirrors natural everyday Hinglish (e.g., "bilkul", "chip-chip", "garmi").
- Keep responses concise and engaging (2-3 paragraphs max, with bullet points where helpful).

STRICT MEDICAL & SENSITIVE STATEMENT CONSTRAINTS (ZERO-TOLERANCE):
1. ZERO UNSUBSTANTIATED MEDICAL STATEMENTS & ZERO MEDICAL DIAGNOSIS:
   - You are a skincare lifestyle concierge, NOT a dermatologist or medical doctor.
   - NEVER diagnose any skin disease or condition (cystic acne, eczema, rosacea, dermatitis, melasma, psoriasis, fungal infections).
   - NEVER make sensitive or medical statements that require clinical fact-checking.
   - NEVER claim that SKIPD products cure, treat, or eradicate medical skin conditions.
   - If a customer mentions persistent skin conditions or disease, explicitly recommend consulting a board-certified dermatologist.
   - For pregnancy or breastfeeding, congratulate them and firmly advise sharing the ingredient list with their OB-GYN or doctor before introducing new actives.
   - For adverse reactions or rashes, immediately advise stopping product use, gently rinsing with cool water, and contacting customer support.

2. ABSOLUTE BAN ON FAIRNESS / WHITENING / COLORISM:
   - NEVER use the words "fairness", "whitening", "skin lightening", or "bleaching".
   - Reject any fairness claims: clarify that SKIPD formulates for skin health, barrier strength, and radiance across all Indian skin tones.

3. PRICING & POLICY INTEGRITY:
   - Products are ₹1,500 each. Do not invent unauthorized discount codes or fabricate delivery dates.
"""

# Try importing sarvamai
try:
    from sarvamai import SarvamAI
    SARVAM_SDK_AVAILABLE = True
except ImportError:
    SARVAM_SDK_AVAILABLE = False

KEY_FILE = os.path.join(os.path.dirname(__file__), ".sarvam_key")

def get_saved_sarvam_key():
    if os.environ.get("SARVAM_API_KEY"):
        return os.environ.get("SARVAM_API_KEY").strip()
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return None

def save_sarvam_key(key):
    try:
        with open(KEY_FILE, "w", encoding="utf-8") as f:
            f.write(key.strip())
        return True
    except Exception as e:
        print(f"Error saving key: {e}")
        return False

# Persistent chat session for multi-turn web chat demo
_active_chat_session = None

class SkipdUnifiedHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, api-subscription-key, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/gemini-info":
            gemini_key = os.getenv("GEMINI_API_KEY")
            info = {
                "gemini_sdk_available": GEMINI_AVAILABLE,
                "has_key": bool(gemini_key),
                "key_preview": (gemini_key[:6] + "..." + gemini_key[-4:]) if gemini_key and len(gemini_key) > 10 else None,
                "default_model": gemini_client.DEFAULT_MODEL if gemini_client else "gemini-3.5-flash-lite",
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(info).encode("utf-8"))
            return

        if parsed.path == "/api/sarvam-info":
            saved_key = get_saved_sarvam_key()
            info = {
                "sdk_installed": SARVAM_SDK_AVAILABLE,
                "has_saved_key": bool(saved_key),
                "key_preview": (saved_key[:6] + "..." + saved_key[-4:]) if saved_key and len(saved_key) > 10 else None,
                "default_model": DEFAULT_MODEL,
                "default_speaker": DEFAULT_SPEAKER,
                "default_language": DEFAULT_LANG,
                "models": SARVAM_MODELS,
                "recommended_speakers": [
                    {"id": "meera", "name": "Meera", "desc": "Warm, natural & reassuring (Concierge Hero)", "gender": "Female"},
                    {"id": "anushka", "name": "Anushka", "desc": "Lively, clear & modern lifestyle", "gender": "Female"},
                    {"id": "kavya", "name": "Kavya", "desc": "Gentle, friendly conversational tone", "gender": "Female"},
                    {"id": "shubh", "name": "Shubh", "desc": "Articulate, confident & smooth narration", "gender": "Male"},
                    {"id": "ratan", "name": "Ratan", "desc": "Calm, grounded & warm tone", "gender": "Male"},
                    {"id": "arvind", "name": "Arvind", "desc": "Professional, articulate guide", "gender": "Male"}
                ]
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(info).encode("utf-8"))
            return

        return super().do_GET()

    def do_POST(self):
        global _active_chat_session
        parsed = urlparse(self.path)

        # ---------------------------------------------------------------------
        # 1. GEMINI TEXT GENERATION
        # ---------------------------------------------------------------------
        if parsed.path == "/api/gemini-generate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                prompt = data.get("prompt", "").strip()
                model = data.get("model") or gemini_client.DEFAULT_MODEL
                api_key = data.get("api_key")

                if not prompt:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Prompt cannot be empty"}).encode("utf-8"))
                    return

                text = gemini_client.generate_text(
                    prompt=prompt,
                    model=model,
                    system_instruction=SKIPD_SYSTEM_PROMPT,
                    api_key=api_key
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"text": text, "model": model, "status": "success"}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        # ---------------------------------------------------------------------
        # 2. GEMINI MULTI-TURN CHAT
        # ---------------------------------------------------------------------
        if parsed.path == "/api/gemini-chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                message = data.get("message", "").strip()
                reset = data.get("reset", False)

                if reset or _active_chat_session is None:
                    _active_chat_session = gemini_client.start_chat(system_instruction=SKIPD_SYSTEM_PROMPT)

                if not message:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ready", "message": "Chat session initialized"}).encode("utf-8"))
                    return

                reply = _active_chat_session.send_message(message)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"reply": reply.text.strip(), "status": "success"}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        # ---------------------------------------------------------------------
        # 3. SARVAM SAVE KEY
        # ---------------------------------------------------------------------
        if parsed.path == "/api/save-key":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                key = data.get("api_key", "").strip()
                if key:
                    save_sarvam_key(key)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "saved", "message": "Sarvam API Key saved successfully"}).encode("utf-8"))
                else:
                    if os.path.exists(KEY_FILE):
                        os.remove(KEY_FILE)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "cleared", "message": "Sarvam API Key removed"}).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        # ---------------------------------------------------------------------
        # 4. SARVAM TEXT TO SPEECH
        # ---------------------------------------------------------------------
        if parsed.path == "/api/sarvam-tts":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Invalid JSON payload: {e}"}).encode("utf-8"))
                return

            text = data.get("text", "").strip()
            if not text:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Text parameter cannot be empty"}).encode("utf-8"))
                return

            api_key = data.get("api_key", "").strip() or self.headers.get("api-subscription-key", "").strip() or get_saved_sarvam_key()
            if not api_key:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "No Sarvam API Key provided.",
                    "help": "Please supply your Sarvam API subscription key in the request or save it in the Founder Studio -> Sarvam AI Voice tab."
                }).encode("utf-8"))
                return

            speaker = data.get("speaker", DEFAULT_SPEAKER)
            model = data.get("model", DEFAULT_MODEL)
            language_code = data.get("language_code") or data.get("target_language_code") or DEFAULT_LANG
            pace = float(data.get("pace", 1.0))
            enable_preprocessing = bool(data.get("enable_preprocessing", True))

            try:
                if SARVAM_SDK_AVAILABLE:
                    client = SarvamAI(api_subscription_key=api_key)
                    response = client.text_to_speech.convert(
                        text=text,
                        language_code=language_code,
                        speaker=speaker,
                        model=model,
                        pace=pace,
                        enable_preprocessing=enable_preprocessing,
                        output_audio_codec="mp3"
                    )
                    raw_audio = response.audios[0]
                    if isinstance(raw_audio, bytes):
                        b64_audio = base64.b64encode(raw_audio).decode("utf-8")
                    else:
                        b64_audio = str(raw_audio)
                else:
                    import requests
                    url = "https://api.sarvam.ai/text-to-speech"
                    headers = {
                        "api-subscription-key": api_key,
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "text": text,
                        "language_code": language_code,
                        "speaker": speaker,
                        "model": model,
                        "pace": pace,
                        "enable_preprocessing": enable_preprocessing,
                        "output_audio_codec": "mp3"
                    }
                    r = requests.post(url, json=payload, headers=headers, timeout=20)
                    if r.status_code != 200:
                        raise Exception(f"Sarvam API responded with HTTP {r.status_code}: {r.text}")
                    res_json = r.json()
                    b64_audio = res_json.get("audios", [""])[0]

                result_payload = {
                    "status": "success",
                    "audios": [b64_audio],
                    "model": model,
                    "speaker": speaker,
                    "language_code": language_code
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result_payload).encode("utf-8"))

            except Exception as e:
                traceback.print_exc()
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run_server(port=3000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, SkipdUnifiedHandler)
    print(f">> SKIPD + Gemini + Sarvam Server active on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    run_server(port)
