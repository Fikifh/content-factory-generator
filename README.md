# Content Factory Generator

> AI-powered TikTok video pipeline that turns a single topic into a **scene-based, voice-narrated, stock-footage-driven video** — fully automated.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-8E75B2)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-reference--implementation-yellow)](#)

A lightweight Python pipeline that:

1. 🧠 **Generates a structured JSON script** using Google Gemini (scene-by-scene narration + visual keywords)
2. 🎙️ **Synthesizes voice-over audio** for each scene using Edge TTS (Indonesian neural voice)
3. 🎬 **Downloads portrait stock footage** from Pexels (vertical 9:16, 720p–1080p)
4. ✂️ **Composes scene clips** by looping/cutting video to match audio length
5. 🎞️ **Stitches the final video** into a 30–40 second TikTok-ready `.mp4`

---

## 🎯 Why this exists

Most TikTok content scripts are copy-pasted. **Content Factory** treats scripts as **structured data** — each scene carries its own narration text and visual keyword, so the pipeline can compose them deterministically without human editing.

Format used: 5-scene "What happens to your body if…" anatomy-explainer formula — high-engagement in the herbal/health niche.

---

## 📦 Repository structure

```
content-factory-generator/
├── main.py              # entry point — orchestrates the full pipeline
├── requirements.txt     # Python dependencies
├── .env.example         # template for GEMINI_API_KEY + PEXELS_API_KEY
├── assets/              # optional local asset overrides (gitignored)
│   ├── audio/
│   └── video/
├── output/              # final rendered videos (gitignored)
└── temp/                # intermediate audio/video files (gitignored)
```

---

## 🚀 Quick start

### 1. Clone and install

```bash
git clone https://github.com/Fikifh/content-factory-generator.git
cd content-factory-generator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env and fill in your real keys:
#   GEMINI_API_KEY — get one at https://aistudio.google.com/app/apikey
#   PEXELS_API_KEY — get one at https://www.pexels.com/api/
```

### 3. Run the pipeline

```bash
python main.py
```

The script will:
1. Generate a 5-scene JSON script for the topic in `main.py` (default: *"Apa yang terjadi pada tubuhmu jika rajin konsumsi jahe, kunyit, sereh dalam seminggu?"*)
2. Fetch Pexels clips for each scene's visual keyword
3. Synthesize Indonesian voice-over
4. Stitch everything into `output/tiktok_smart_scene.mp4`

---

## 🛠️ How it works

```
[Topic String]
     │
     ▼
┌─────────────────────────────┐
│ Gemini 2.5 Flash            │
│ → JSON array of scenes      │
│   [{text, keyword}, ...]    │
└────────┬────────────────────┘
         │
         ├─► [Edge TTS] ──► audio_0.mp3, audio_1.mp3, ...
         │
         ├─► [Pexels API] ──► video_0.mp4, video_1.mp4, ...
         │
         ▼
┌─────────────────────────────┐
│ MoviePy scene composer      │
│ → loop/cut video to audio   │
│ → resize 9:16 (1080×1920)   │
│ → set audio                 │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Final concat + render       │
│ → output/tiktok_smart_      │
│   scene.mp4 (h264 + aac)    │
└─────────────────────────────┘
```

Each scene runs independently, so retries are cheap — if a single Pexels clip fails, you can re-run the failed scene alone.

---

## 🧪 Tested with

- Python 3.10+
- Gemini 2.5 Flash (`google-genai`)
- Edge TTS (`edge-tts`)
- MoviePy 1.x / 2.x
- Pexels API (free tier: 200 requests/hour, 20k/month)

---

## ⚙️ Configuration

All configuration lives in `.env`:

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | _(required)_ | Google Gemini API key |
| `PEXELS_API_KEY` | _(required)_ | Pexels API key |
| `TIKTOK_VOICE` | `id-ID-ArdiNeural` | Edge TTS voice (Indonesian neural male) |
| `TIKTOK_SPEED` | `+10%` | Voice rate adjustment |

Other constants in `main.py`:
- `TOPIC` (line 200) — the topic string passed to Gemini. Edit to test different content.
- Scene length (30–40s) — controlled by the prompt template.

---

## 🛡️ Compliance & Safety

This generator is a **content draft tool**, not an auto-publisher. The user is responsible for:

- Verifying any health/medical claims (the prompt explicitly nudges toward PIRT-registered products and avoids overclaims)
- Reviewing generated scripts before publishing
- Complying with TikTok's Terms of Service and affiliate disclosure rules

This pipeline **does not** post automatically to TikTok or any social platform.

---

## 📜 License

[MIT](LICENSE) — © 2026 Fiki Firmansyah

---

## 🔗 Related projects

- **[AI TikTok Affiliate Intelligence Platform](https://github.com/Fikifh/AiTiktokAffiliateIntelligencePlatform)** — the production-grade TypeScript successor to this pipeline. NestJS + Next.js + multi-agent AI orchestration + 13-category policy safety scanner.
