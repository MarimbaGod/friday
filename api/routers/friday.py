from fastapi import APIRouter, HTTPException, UploadFile, File, Response
import requests
import os
import json
from openai import OpenAI
from pathlib import Path
from datetime import datetime
import random
import string


router = APIRouter()
client = OpenAI()
openai_api_key = os.getenv("OPENAI_API_KEY")
output_folder = Path(__file__).parent / "output" # Saved output folder
transcript_file = Path(__file__).parent / "transcript.md" #path to transcript

def append_to_transcript(user_input: str, ai_response: str):
    with open(transcript_file, "a") as file:
        file.write(f"User: {user_input}\AI: {ai_response}\n\n")

def generate_unique_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{timestamp}_{random_str}"


# Use the gpt4 model
@router.post("/friday")
async def ask_friday(user_input: str, conversation_history: str = None):
    chat_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    if conversation_history in [None, "", "[]"]:
        messages = []
    else:
        try:
            messages = json.loads(conversation_history)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid Conversation history format")

    messages.append({"role": "user", "content": user_input})

    payload = {
        "model": "gpt-4-0125-preview",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 150
    }

    try:
        response = requests.post(chat_url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        friday_response = response_data['choices'][0]['message']['content'].strip()

        append_to_transcript(user_input, friday_response)

        #TTS API call
        unique_id = generate_unique_id()
        speech_file_path = output_folder / f"{unique_id}.mp3"
        tts_response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=friday_response
        )
        tts_response.stream_to_file(str(speech_file_path))

        audio_url = f"/friday/audio/{unique_id}.mp3"
        return {
            "text_response": friday_response,
            "audio_url": audio_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/friday/audio/{filename}")
async def friday_audio(filename: str):
    file_path = output_folder / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return Response(content=file_path.read_bytes(), media_type="audio/mpeg")

@router.post("/friday/input")
async def speech_to_text(audio_file: UploadFile = File(...)):
    try:
        #save temp
        temp_file_path = f"temp_{audio_file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(await audio_file.read())

        #Openai Audio Transcription API
        with open(temp_file_path, "rb") as f:
            transcribed_text = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text"
            )
        # remove temp storage
        os.remove(temp_file_path)

        #Debug
        return transcribed_text

    except Exception as e:
        print("Error occurred:", str(e))
        raise HTTPException(status_code=500, detail=f"Transcription Failed: {str(e)}")
