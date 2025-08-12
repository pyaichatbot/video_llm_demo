
import os
import ffmpeg
import glob
import requests
import json
from dotenv import load_dotenv

load_dotenv()

AZURE_GPT_ENDPOINT = os.getenv("AZURE_GPT_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")

def extract_audio(video_file, audio_file="audio.wav"):
    ffmpeg.input(video_file).output(audio_file, acodec="pcm_s16le", ac=1, ar="16k").run(overwrite_output=True)
    return audio_file

def extract_frames(video_file, fps=0.2):
    os.makedirs("frames", exist_ok=True)
    ffmpeg.input(video_file).filter("fps", fps=fps).output("frames/frame_%04d.png").run(overwrite_output=True)
    return sorted(glob.glob("frames/frame_*.png"))

def stt_whisper(audio_file):
    with open(audio_file, "rb") as f:
        resp = requests.post("http://localhost:9000/asr", files={"file": f})
    resp.raise_for_status()
    return resp.json().get("text", "")

def caption_image(image_file):
    with open(image_file, "rb") as f:
        resp = requests.post("http://localhost:5001/caption", files={"file": f})
    resp.raise_for_status()
    return resp.json().get("caption", "")

def call_gpt(prompt):
    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI assistant skilled in summarizing multimodal content."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 700
    }
    headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
    r = requests.post(f"{AZURE_GPT_ENDPOINT}/chat/completions?api-version=2023-06-01",
                      headers=headers, data=json.dumps(payload))
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

if __name__ == "__main__":
    video_file = "sample.mp4"  # replace with your video file
    print("🎥 Extracting audio...")
    audio_file = extract_audio(video_file)

    print("🖼 Extracting frames...")
    frames = extract_frames(video_file)

    print("📝 Transcribing audio...")
    transcript = stt_whisper(audio_file)

    print("🖼 Captioning frames...")
    captions = []
    for frame in frames[:5]:  # limit to 5 frames for demo
        cap = caption_image(frame)
        captions.append(cap)

    combined_prompt = f"""Here is the transcript: {transcript}
    And here are visual captions: {', '.join(captions)}
    Please summarize both into a coherent description."""

    print("🤖 Calling GPT...")
    summary = call_gpt(combined_prompt)
    print("Summary:", summary)
