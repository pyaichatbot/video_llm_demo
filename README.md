
# Video LLM Demo – Transcript and Hybrid Approaches

## Requirements
- Python 3.9+
- ffmpeg installed locally
- Local Whisper STT service at http://localhost:9000/asr
- Local Image Captioning service for Hybrid at http://localhost:5001/caption
- Azure OpenAI API credentials in .env

## Files
- video_to_transcript.py → Audio-only transcript to GPT
- hybrid_video_analysis.py → Audio transcript + frame captions to GPT
- requirements.txt
- .env.example

## How to Run
1. `pip install -r requirements.txt`
2. Set up `.env` with your Azure GPT endpoint and key.
3. Start local STT (Whisper) and image captioning containers.
4. Place `sample.mp4` in the same folder.
5. Run:
   - Audio only: `python video_to_transcript.py`
   - Hybrid: `python hybrid_video_analysis.py`
