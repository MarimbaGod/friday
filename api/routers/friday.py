from fastapi import APIRouter, HTTPException
import requests
import os
import json


router = APIRouter()

openai_api_key = os.getenv("OPENAI_API_KEY")

# Use the gpt4
@router.post("/friday")
async def ask_friday(user_input: str, conversation_history: str = None):
    url = "https://api.openai.com/v1/chat/completions"
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
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        friday_response = response_data['choices'][0]['message']['content'].strip()
        return {"response": friday_response}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/friday/speech")
# async def speech_to_friday()
