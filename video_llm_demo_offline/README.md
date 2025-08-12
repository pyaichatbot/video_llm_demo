# Video LLM Demo – Fully Offline STT/Captions + Self-hosted GPT + TTS

This package runs **two demos** completely offline for STT/captioning/TTS (only GPT calls leave the box, and you can point to your self-hosted GPT).

## What’s Included
- **Local STT**: Whisper (switchable `tiny`/`base` via `.env`)
- **Local Image Captioning**: BLIP (Salesforce/blip-image-captioning-base by default)
- **TTS**: Kitty/Kitten TTS (pre-warmed voice cache)
- **Sample Video**: `sample.mp4` (5s visuals; scripts can overlay/replace audio at runtime if desired)
- **Two scripts**:
  - `video_to_transcript.py` → Video audio → Whisper → GPT → TTS
  - `hybrid_video_analysis.py` → Video audio → Whisper + frames → BLIP captions → GPT → TTS

## 1) Configure
Copy `.env.example` to `.env` and edit:
```bash
AZURE_GPT_ENDPOINT=https://<your-endpoint>/openai/deployments/<your-deployment>
AZURE_API_KEY=<key or token>
WHISPER_MODEL=tiny           # or base
BLIP_MODEL=Salesforce/blip-image-captioning-base
KITTY_VOICE=en_US/blizzard_fem
```

## 2) Build
```bash
docker build -t video-llm-demo .
```

> The build **pre-downloads** Whisper (tiny & base), BLIP base model, and warms TTS cache → ready for offline demos.

## 3) Run – Audio-only (Transcript) Demo
```bash
docker run --rm -v %cd%:/app --env-file .env video-llm-demo python video_to_transcript.py
# on mac/linux: use $(pwd) instead of %cd%
```

## 4) Run – Hybrid (Audio + Visual) Demo
```bash
docker run --rm -v %cd%:/app --env-file .env video-llm-demo python hybrid_video_analysis.py
```

## Notes
- Place your short demo video as `sample.mp4` in this folder (a default sample is provided). Keep it **5–10s** for live speed.
- For **Whisper model switching**, just edit `.env` (`tiny` ↔ `base`). No rebuild required.
- For **BLIP model change**, use `.env` `BLIP_MODEL`. If not cached, it will download at first run (requires network).

## Troubleshooting (Live)
- **CUDA not available**: This build uses **CPU** Torch; performance is demo-grade for short clips.
- **No audio device in container**: TTS writes to a `response.wav`. Play it on host after the run (the script saves to repo root).
- **Corp proxy**: Add `--build-arg` HTTP(S)_PROXY if needed and set Docker daemon proxy.
