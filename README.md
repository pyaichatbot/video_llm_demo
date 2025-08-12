
# Video LLM Demo – Audio and Hybrid with STT + GPT + TTS

## Prerequisites (handled by Docker)
- ffmpeg
- Python 3.10
- Pinned dependencies in requirements.txt

## Services in docker-compose
- **whisper**: Local STT (whisper-tiny)
- **kittentts**: Local TTS
- **app**: Your GPT demo app

## Build & Run
1. Copy `.env.example` to `.env` and fill with your Azure GPT endpoint and API key.
2. Place `sample.mp4` in this directory.
3. Build and start services:
   ```bash
   docker compose up --build
   ```
4. Run audio-only demo:
   ```bash
   docker compose run --rm app python video_to_transcript.py
   ```
5. Run hybrid demo:
   ```bash
   docker compose run --rm app python hybrid_video_analysis.py
   ```

## Notes
- The app container uses `network_mode: host` to communicate with Whisper (9000) and KittenTTS (5002).
- For hybrid mode, you must also have an image captioning service at `http://localhost:5001/caption`.
