# SKIPD — Skipcare™ for Modern Urban India
> **AI Skincare Concierge, Founder Operations Studio & Voice Agent**
> Cutting through 10-step skincare clutter with smarter, single-swipe stick formulations engineered for Indian weather.

---

## 🌟 Overview

**SKIPD** is an Indian D2C beauty & lifestyle brand revolutionizing daily skincare through **Skipcare™**—replacing cumbersome 5-to-10 step routines with high-performance, heat-resilient stick formulations:

1. **Glowscreen (Morning Glow Stick — ₹1,500)**: SPF 50+ broad spectrum, invisible multi-molecular day shield combining toner, serum, moisturiser, and sun protection without greasy white cast on Indian Fitzpatrick skin tones III–VI.
2. **Moonscreen (Overnight Recovery Balm — ₹1,500)**: Concentrated overnight barrier repair powered by triple ceramides (NP, AP, EOP), signal peptides, and plant squalane to lock in moisture and reverse pollution/barrier fatigue.

The web platform features an **AI Skincare Concierge & Founder Operations Studio** powered by **Google Gemini** (with multi-turn conversational intelligence) and **Sarvam AI Voice TTS** (natural Indian accent speech in Hinglish/English).

---

## ✨ Features

- **🛍️ Modern Product Showcase**: High-res imagery, verified ingredient matrices, real climate resilience (tested to survive 45°C Indian summer heat).
- **🤖 AI Skincare Concierge**:
  - Multi-turn conversational recommendations.
  - Natural Hinglish understanding (*"chip-chip"*, *"garmi"*, *"routine clutter"*).
  - Built-in Fallback Rule Engine with 15 production FAQs and instant answers.
- **🛡️ Strict Medical & Clinical Safety Guardrails**:
  - **Zero-Tolerance Medical Constraint**: Never diagnoses skin diseases (cystic acne, eczema, rosacea, melasma). Refers users to board-certified dermatologists.
  - **Pregnancy & Lactation Protocol**: Advises consulting an OB-GYN before introducing active ingredients.
  - **Absolute Colorism/Whitening Ban**: Zero tolerance for "fairness", "whitening", or "bleaching" claims—focuses exclusively on barrier health and natural radiance.
  - **Adverse Reaction Escalation**: Immediate soothing triage and direct escalation to founder customer support.
- **🎙️ Voice Synthesis with Sarvam AI**:
  - High-fidelity Indic text-to-speech (*bulbul:v3* and *bulbul:v2*).
  - Native Indian speakers (Meera, Anushka, Kavya, Shubh, Ratan, Arvind).
- **💼 Founder Operations Studio**:
  - Live inspection of chat history and customer inquiries.
  - Escalation alert banner with lead capture (Name, Email, Order ID).
  - Instant pre-configured founder evaluation test prompts.

---

## 🏗️ Architecture

```
skipd-bot/
├── index.html                # Responsive storefront & AI Concierge interface
├── style.css                 # Premium dark luxury & warm gold styling
├── app.js                    # Client-side state, FAQ engine, UI interactions
├── server.py                 # Python HTTP server & API proxy
├── gemini_client.py          # Google Gen AI SDK integration (Gemini 3.5 Flash Lite)
├── test_gemini.py            # Gemini integration test suite
├── test_guardrails_gemini.py # Medical & safety guardrail tests
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
└── assets/                   # Product imagery, avatars, and audio samples
```

---

## 🚀 Quick Start (Local Run)

### 1. Clone the Repository
```bash
git clone https://github.com/Anantgupta23/skipd-app.git
cd skipd-app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Copy `.env.example` to `.env` and insert your API keys:
```bash
cp .env.example .env
```
In `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here # Optional
```

### 4. Start the Application
```bash
python server.py
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 🌐 Deploy to GitHub Pages (Static Mode)

The frontend (`index.html`, `style.css`, `app.js`) is fully functional as a static web application. In static hosting mode, the interactive FAQ rule engine, audio player, founder screening tests, and UI work directly in the browser!

To enable GitHub Pages:
1. Go to repository **Settings** > **Pages**.
2. Under **Build and deployment** > **Source**, select **Deploy from a branch**.
3. Branch: `main` / Folder: `/(root)`.
4. Click **Save**.

---

## 🔒 Security & Privacy

- Keys and credentials are strictly kept local via `.gitignore` (`.env`, `.sarvam_key`).
- No sensitive user personal data or tokens are committed to version control.

---

## 📄 License

MIT License. Crafted for SKIPD Skipcare™ Operations.
