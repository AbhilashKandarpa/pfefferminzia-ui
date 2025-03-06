from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
import requests
import os
import time  

app = FastAPI()

API_KEY = os.getenv("ALAN_API_KEY")
headers = {"Authorization": f"Bearer {API_KEY}"}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_response():
    """ Antwort von Alan API wirklich als Stream ausgeben """
    url = "https://app.alan.de/api/v1/llm/generate_stream"
    payload = json.dumps({
        "messages": [
            {"content": input, "role": "user"}
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800,
        "model": "comma-soft/comma-llm-l-v3"
    })

    response = requests.post(url, headers=headers, data=payload, stream=True)

    for chunk in response.iter_content(chunk_size=64): 
        if chunk:
            yield chunk.decode()  
            time.sleep(0.1) 

@app.post("/stream")
async def stream_response(request: Request):
    data = await request.json()
    user_input = data.get("input", "")
    return StreamingResponse(generate_response(user_input), media_type="text/plain")
