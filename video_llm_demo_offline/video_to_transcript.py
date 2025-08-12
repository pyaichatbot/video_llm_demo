import os, json, tempfile, ffmpeg
from dotenv import load_dotenv
import whisper
from pydub import AudioSegment
from kitty_tts import TTS
import requests

load_dotenv()

AZURE_GPT_ENDPOINT = os.getenv("AZURE_GPT_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")
KITTY_VOICE = os.getenv("KITTY_VOICE", "en_US/blizzard_fem")

SAMPLE_VIDEO = "sample.mp4"

def extract_audio(video_path, wav_out="audio.wav"):
    (
        ffmpeg
        .input(video_path)
        .output(wav_out, acodec="pcm_s16le", ac=1, ar="16000")
        .overwrite_output()
        .run(quiet=True)
    )
    return wav_out

def transcribe(audio_path):
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(audio_path, language="en")
    return result.get("text","").strip()

def call_gpt(prompt):
    payload = {
        "messages": [
            {"role": "system", "content": "You are a concise assistant for meeting/video summaries."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }
    headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
    r = requests.post(f"{AZURE_GPT_ENDPOINT}/chat/completions?api-version=2023-06-01",
                      headers=headers, data=json.dumps(payload), timeout=120)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]

def synthesize(text, out_wav="response.wav"):
    tts = TTS()
    tts.synthesize_to_file(text, out_wav)
    return out_wav

if __name__ == "__main__":
    assert os.path.exists(SAMPLE_VIDEO), "Place a sample.mp4 in the repo root."
    print("🎥 Extracting audio…")
    wav = extract_audio(SAMPLE_VIDEO)

    print("📝 Transcribing with Whisper (%s) …" % WHISPER_MODEL)
    transcript = transcribe(wav)
    print("Transcript:", transcript[:300], "…" if len(transcript)>300 else "")

    print("🤖 Calling GPT (summary)…")
    summary = call_gpt(f"Summarize this transcript in 3 bullets, plain English:\n{transcript}" )
    print("\n=== GPT SUMMARY ===\n", summary)

    print("🔊 TTS synthesizing response to response.wav …")
    out = synthesize(summary, "response.wav")
    print("Saved:", out)
