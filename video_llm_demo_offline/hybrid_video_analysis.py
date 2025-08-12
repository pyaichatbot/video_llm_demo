import os, glob, json, ffmpeg, torch
from dotenv import load_dotenv
import whisper
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from kitty_tts import TTS
import requests

load_dotenv()

AZURE_GPT_ENDPOINT = os.getenv("AZURE_GPT_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")
BLIP_MODEL = os.getenv("BLIP_MODEL", "Salesforce/blip-image-captioning-base")

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

def extract_frames(video_path, fps=0.5):
    os.makedirs("frames", exist_ok=True)
    (
        ffmpeg
        .input(video_path)
        .filter("fps", fps=fps)
        .output("frames/frame_%03d.png")
        .overwrite_output()
        .run(quiet=True)
    )
    return sorted(glob.glob("frames/frame_*.png"))

def transcribe(audio_path):
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(audio_path, language="en")
    return result.get("text","").strip()

def caption_images(paths):
    device = "cpu"
    processor = BlipProcessor.from_pretrained(BLIP_MODEL)
    model = BlipForConditionalGeneration.from_pretrained(BLIP_MODEL).to(device)
    caps = []
    for p in paths[:5]:
        image = Image.open(p).convert("RGB")
        inputs = processor(image, return_tensors="pt").to(device)
        out = model.generate(**inputs, max_new_tokens=30)
        text = processor.decode(out[0], skip_special_tokens=True)
        caps.append(text)
    return caps

def call_gpt(prompt):
    payload = {
        "messages": [
            {"role": "system", "content": "You summarize video content from transcript and keyframe captions."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 400
    }
    headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
    r = requests.post(f"{AZURE_GPT_ENDPOINT}/chat/completions?api-version=2023-06-01",
                      headers=headers, data=json.dumps(payload), timeout=180)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]

def synthesize(text, out_wav="response.wav"):
    tts = TTS()
    tts.synthesize_to_file(text, out_wav)
    return out_wav

if __name__ == "__main__":
    assert os.path.exists(SAMPLE_VIDEO), "Place a sample.mp4 in the repo root."
    print("🎥 Extracting audio & frames…")
    wav = extract_audio(SAMPLE_VIDEO)
    frames = extract_frames(SAMPLE_VIDEO, fps=0.5)
    print(f"Frames extracted: {len(frames)}")

    print("📝 Transcribing with Whisper (%s) …" % WHISPER_MODEL)
    transcript = transcribe(wav)
    print("Transcript preview:", transcript[:200], "…" if len(transcript)>200 else "")

    print("🖼 Captioning key frames with BLIP …")
    captions = caption_images(frames)
    print("Captions:", captions)

    prompt = f"""Use both sources to summarize:
Transcript: {transcript}
Frame captions: {captions}
Return 4 clear bullet points and a 1-sentence overall summary."""

    print("🤖 Calling GPT …")
    summary = call_gpt(prompt)
    print("\n=== HYBRID SUMMARY ===\n", summary)

    print("🔊 TTS synthesizing summary → response.wav …")
    out = synthesize(summary, "response.wav")
    print("Saved:", out)
