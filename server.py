from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import Alan
from create_links import fetch_article_url
from extract_filenames import extract_document_names


# Load environment variables
load_dotenv()

app = FastAPI(
    title="Chat API",
    description="API for streaming chat responses from Alan AI",
    version="1.0.0"
)

API_KEY = os.getenv("ALAN_API_KEY")
if not API_KEY:
    raise ValueError("ALAN_API_KEY environment variable not set")

headers = {"Authorization": f"Bearer {API_KEY}"}

# Allow requests from frontend (React)
origins = [
    "*"  # Add your frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow only frontend origin
    allow_credentials=True,  # Allow credentials (e.g., cookies, authentication)
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

def truncate_answer(text):
    # Define the truncation point
    cutoff_phrase = "\n\nFolgende Dokumente der Wissensdatenbank"
    
    # Find the cutoff index
    cutoff_index = text.find(cutoff_phrase)

    # If the phrase is found, truncate the text before it
    if cutoff_index != -1:
        return text[:cutoff_index]
    
    # If the phrase is not found, return the original text
    return text

def process(full_response):
    documents = extract_document_names(full_response)
    urls =[]
    for document in documents:
        url = fetch_article_url(document)
        urls.append(f"{url}\n")
    full_response = truncate_answer(full_response)
    full_response += f"\n\n{urls}"
    print(f"{full_response}")
    return full_response


@app.get("/stream")
async def stream():
    return {"message": "CORS is working!"}

# Request model
class ChatInput(BaseModel):
    input: str

    class Config:
        schema_extra = {
            "example": {
                "input": "Tell me about machine learning"
            }
        }


@app.post("/stream",
    summary="Chat response",
    description="Send a message and receive a complete response from the AI"
)
async def stream_response(chat_input: ChatInput):
    if not chat_input.input.strip():
        raise HTTPException(status_code=400, detail="Input field cannot be empty")
    
    # Get complete response
    response = Alan.generate_response(chat_input.input)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"API request failed with status code {response.status_code}"
        )

    # Collect all chunks into a single response
    full_response = ""
    for chunk in response.iter_content(chunk_size=64):
        if chunk:
            full_response += chunk.decode("utf-8", errors="ignore")

    # Return as plain text
    full_response = process(full_response)
    return full_response


@app.post("/start_chat",
    summary="Chat response",
    description="Send a message and receive a complete response from the AI"
)
async def create_chat(chat_input: ChatInput):
    if not chat_input.input.strip():
        raise HTTPException(status_code=400, detail="Input field cannot be empty")
    
    # Get complete response
    response = Alan.create_chat(chat_input.input)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"API request failed with status code {response.status_code}"
        )

    # Collect all chunks into a single response
    full_response = ""
    for chunk in response.iter_content(chunk_size=64):
        if chunk:
            full_response += chunk.decode("utf-8", errors="ignore")

    # Return as plain text
    print(f"{full_response}")
    return full_response    


@app.post("/continue_chat",
    summary="Chat response",
    description="Send a message and receive a complete response from the AI"
)
async def continue_chat(chat_input: ChatInput):
    if not chat_input.input.strip():
        raise HTTPException(status_code=400, detail="Input field cannot be empty")
    
    # Get complete response
    response = Alan.continue_chat(chat_input.input, Alan.chat_id, Alan.previous_message_id)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"API request failed with status code {response.status_code}"
        )

    # Collect all chunks into a single response
    full_response = ""
    for chunk in response.iter_content(chunk_size=64):
        if chunk:
            full_response += chunk.decode("utf-8", errors="ignore")

    # Return as plain text
    print(f"{full_response}")
    return full_response 


@app.get("/health",
    summary="Health check",
    description="Check if the API is running"
)
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    