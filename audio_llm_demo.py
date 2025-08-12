import requests
import subprocess
import json
import os

AZURE_GPT_ENDPOINT = os.getenv("AZURE_GPT_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")

def record_audio(filename="audio/input.wav", duration=5):
    subprocess.run(["ffmpeg", "-y", "-f", "avfoundation", "-i", ":0", "-t", str(duration), filename])

def stt_whisper(filename):
    files = {"file": open(filename, "rb")}
    r = requests.post("http://localhost:9000/asr", files=files)
    return r.json().get("text", "")

def call_gpt(prompt):
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 200
    }
    headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
    r = requests.post(f"{AZURE_GPT_ENDPOINT}/chat/completions?api-version=2023-06-01", 
                      headers=headers, data=json.dumps(payload))
    return r.json()["choices"][0]["message"]["content"]

def tts_kittentts(text, outfile="audio/output.wav"):
    r = requests.post("http://localhost:5002/api/tts", json={"text": text})
    with open(outfile, "wb") as f:
        f.write(r.content)
    subprocess.run(["ffplay", "-nodisp", "-autoexit", outfile])

if __name__ == "__main__":
    print("🎤 Recording speech...")
    record_audio()

    print("📝 Transcribing speech...")
    text_input = stt_whisper("audio/input.wav")
    print(f"Transcribed: {text_input}")

    print("🤖 Sending to GPT...")
    gpt_response = call_gpt(text_input)
    print(f"GPT Response: {gpt_response}")

    print("🔊 Converting to speech...")
    tts_kittentts(gpt_response)


#     requests==2.31.0
# ffmpeg-python==0.2.0
# python-dotenv==1.0.0

# docker pull ghcr.io/ggerganov/whisper.cpp:latest
# docker tag ghcr.io/ggerganov/whisper.cpp:latest myregistry.company.com/whisper.cpp:latest
# docker push myregistry.company.com/whisper.cpp:latest


# version: '3.8'
# services:
#   whisper:
#     image: ghcr.io/ggerganov/whisper.cpp:latest
#     command: ["--model", "tiny.en", "--language", "en"]
#     ports:
#       - "9000:9000"
#     volumes:
#       - ./audio:/audio

#   kittentts:
#     image: ghcr.io/coqui-ai/kitty-tts:latest
#     ports:
#       - "5002:5002"