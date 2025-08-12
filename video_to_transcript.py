
import os
import ffmpeg
import requests
import json
from dotenv import load_dotenv

load_dotenv()

AZURE_GPT_ENDPOINT = os.getenv("AZURE_GPT_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")

def extract_audio(video_file, audio_file="audio.wav"):
    ffmpeg.input(video_file).output(audio_file, acodec="pcm_s16le", ac=1, ar="16k").run(overwrite_output=True)
    return audio_file

def stt_whisper(audio_file):
    with open(audio_file, "rb") as f:
        resp = requests.post("http://localhost:9000/asr", files={"file": f})
    resp.raise_for_status()
    return resp.json().get("text", "")

def call_gpt(prompt):
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 500
    }
    headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
    r = requests.post(f"{AZURE_GPT_ENDPOINT}/chat/completions?api-version=2023-06-01",
                      headers=headers, data=json.dumps(payload))
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

if __name__ == "__main__":
    video_file = "sample.mp4"  # replace with your video file
    print("🎥 Extracting audio from video...")
    audio_file = extract_audio(video_file)

    print("📝 Transcribing audio...")
    transcript = stt_whisper(audio_file)
    print("Transcript:", transcript)

    print("🤖 Summarizing with GPT...")
    summary = call_gpt(f"Summarize this transcript: {transcript}")
    print("Summary:", summary)
