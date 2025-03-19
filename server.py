from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from time import sleep
from dotenv import load_dotenv
import Alan
from create_links import fetch_article_url
from extract_filenames import extract_document_names
from extract_chat_info import extract_required_info


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
    """
    Truncates the response text at a specific phrase.

    Args:
        text (str): The full response text from the AI

    Returns:
        str: The truncated text without the document references section

    Example:
        >>> truncate_answer("Some answer...\n\nFolgende Dokumente der Wissensdatenbank...")
        "Some answer..."
    """
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
    """
    Processes the full response from Alan AI by extracting document references,
    fetching their URLs, and formatting the final response.

    Args:
        full_response (str): The complete response from Alan AI

    Returns:
        str: Processed response with truncated text and appended document URLs

    Example:
        >>> process("Answer with document references...")
        "Answer...\n\n[URL1]\n[URL2]"
    """
    documents = extract_document_names(full_response)
    urls =[]
    for document in documents:
        url = fetch_article_url(document)
        sleep(1)
        urls.append(f"{url}\n")
    full_response = truncate_answer(full_response)
    full_response += f"\n\n{urls}"
    print(f"{full_response}")
    return full_response


@app.get("/stream")
async def stream():
    """
    Simple endpoint to test if CORS is properly configured.

    Returns:
        dict: A message indicating CORS is working

    Example:
        >>> await stream()
        {"message": "CORS is working!"}
    """
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
    """
    Handles chat messages and returns AI responses.

    Args:
        chat_input (ChatInput): The user's input message

    Returns:
        str: Processed response from the AI

    Raises:
        HTTPException: If input is empty or API request fails

    Example:
        >>> await stream_response(ChatInput(input="Tell me about insurance"))
        "Here's information about insurance..."
    """
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
    """
    Initiates a new chat session with Alan AI.

    Args:
        chat_input (ChatInput): The initial message to start the chat

    Returns:
        str: The AI's response to the initial message

    Raises:
        HTTPException: If input is empty or API request fails

    Example:
        >>> await create_chat(ChatInput(input="Hello"))
        "Hi! How can I help you today?"
    """
    if not chat_input.input.strip():
        raise HTTPException(status_code=400, detail="Input field cannot be empty")
    
    # Get complete response
    response = Alan.create_chat(chat_input.input)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"API request failed with status code {response.status_code}"
        )
        
    chat_id, message_id, message_content = extract_required_info(response.text)

    # Print results
    print("Chat ID:", chat_id)
    print("Message ID:", message_id)
    Alan.save_state(chat_id, str(message_id))
    print("Message Content:", message_content)

    # Return as plain text
    print(f"{message_content}")
    return message_content    


@app.post("/continue_chat",
    summary="Chat response",
    description="Send a message and receive a complete response from the AI"
)
async def continue_chat(chat_input: ChatInput):
    """
    Continues an existing chat session with Alan AI.

    Args:
        chat_input (ChatInput): The next message in the conversation

    Returns:
        str: The AI's response to the message

    Raises:
        HTTPException: If input is empty or API request fails

    Example:
        >>> await continue_chat(ChatInput(input="Tell me more"))
        "Here's additional information..."
    """
    if not chat_input.input.strip():
        raise HTTPException(status_code=400, detail="Input field cannot be empty")
    
    #Load chat and message Ids
    state = Alan.load_state()
    chat_id = state["chat_id"]
    previous_message_id = state["previous_message_id"]
    # Get complete response
    response = Alan.continue_chat(chat_input.input, chat_id, previous_message_id)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"API request failed with status code {response.status_code}"
        )
        
    chat_id, message_id, message_content = extract_required_info(response.text)

    # Print results
    print("Chat ID:", chat_id)
    print("Message ID:", message_id)
    Alan.save_state(chat_id, str(message_id))
    print("Message Content:", message_content)

    # Return as plain text
    print(f"{message_content}")
    return message_content


@app.get("/health",
    summary="Health check",
    description="Check if the API is running"
)
async def health_check():
    """
    Checks if the API service is running properly.

    Returns:
        dict: Status indicating the health of the service

    Example:
        >>> await health_check()
        {"status": "healthy"}
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    