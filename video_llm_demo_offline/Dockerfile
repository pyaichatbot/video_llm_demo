FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive     PIP_NO_CACHE_DIR=1     PYTHONUNBUFFERED=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg espeak-ng git build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# Cache models at build time (both whisper tiny & base; BLIP base)
RUN python - <<'PY'
import whisper
for m in ['tiny','base']:
    print('Downloading whisper model:', m)
    whisper.load_model(m)
print('✅ Whisper models cached')
from transformers import BlipProcessor, BlipForConditionalGeneration
print('Downloading BLIP model: Salesforce/blip-image-captioning-base')
BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')
print('✅ BLIP cached')
PY

# Pre-cache a TTS voice by doing a one-time synthesis (wav discarded)
RUN python - <<'PY'
from pathlib import Path
from kitty_tts import TTS
tts = TTS()
tts.synthesize_to_file('Voice cache warm-up for demo.', 'warmup.wav')
Path('warmup.wav').unlink(missing_ok=True)
print('✅ TTS voice cached')
PY

# App files
COPY . .

# Create an initial sample.mp4 with visuals (without speech). At runtime scripts can override/add speech if needed.
# (We keep it simple here; the repo includes a ready sample.mp4 too.)
CMD [ "bash", "-lc", "python video_to_transcript.py" ]
