import json
import os
import time
import create
import requests
import datetime
from extract_chat_info import extract_required_info
from get_posts import fetch_wordpress_posts
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALAN_API_KEY")
headers = {"Authorization": f"Bearer {API_KEY}"}
connector_id = "0b484b74-06e6-4e11-9389-a2088f12e99c"
knowledge_base_ids = os.getenv("KNOWLEDGE_BASE_IDS")
chat_id = os.getenv("CHAT_ID")
previous_message_id = os.getenv("PREVIOUS_MESSAGE_ID")

# File to store values
STATE_FILE = "chat_state.json"

_files = []
def upload_file(file_name):
    """
    Upload a file to the Alan AI platform.
    
    Args:
        file_name (str): Path to the file to be uploaded
        
    Returns:
        requests.Response: Response object containing the upload result
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        requests.RequestException: If the upload request fails
    """
    url = "https://app.alan.de/api/v1/files/"

    # Open the file and send it as a multipart form
    with open(file_name, "rb") as f:
        files = {
            'file': (file_name, f, "type=application/json")
        }

        response = requests.post(url,
                                 headers=headers,
                                 files=files,
                                 timeout=120,
                                 verify=False)

    return response

def get_uploaded_files():
    """
    Retrieve a list of all files uploaded to the Alan AI platform.
    
    Returns:
        requests.Response: Response containing list of uploaded files
        
    Note:
        Limit is set to 25000 files per request
    """
    url = "https://app.alan.de/api/v1/files/?limit=25000"
    
    response = requests.get(url, headers=headers)

    return response

def create_knowledge_base(connector_id, _files):
    """
    Create a new knowledge base with specified files.
    
    Args:
        connector_id (str): ID of the connector to create knowledge base for
        _files (list): List of file IDs to include in knowledge base
        
    Returns:
        requests.Response: Response containing the created knowledge base info
        
    Example:
        >>> files = ["file_id_1", "file_id_2"]
        >>> response = create_knowledge_base("connector_123", files)
    """
    url = f"https://app.alan.de/api/v1/connectors/{connector_id}/knowledge-bases"

    payload = json.dumps({
        "title": "Pfefferminzia artikeln",
        "description": "Pfefferminzia artikeln",
        "settings": {
          "kind": "file",
          "files": _files
        }
    })

    response = requests.post(url, headers=headers, data=payload)

    return response

def delete_knowledge_base(knowledge_base_id):
    """
    Delete a specific knowledge base.
    
    Args:
        knowledge_base_id (str): ID of the knowledge base to delete
        
    Returns:
        requests.Response: Response indicating deletion status
    """
    url = f"https://app.alan.de/api/v1/connectors/{connector_id}/knowledge-bases/{knowledge_base_id}"

    response = requests.delete(url, headers=headers)

    return response

def generate_response(user_input):
    """
    Generate an AI response using the Alan platform.
    
    Args:
        user_input (str): User's question or prompt
        
    Returns:
        requests.Response: Response containing generated answer
        
    Note:
        Uses comma-llm-l-v3 model with temperature 0.7 and top_p 0.95
    """
    url = "https://app.alan.de/api/v1/llm/generate_stream"

    payload = json.dumps({
    "messages": [
      {
        "content": "What is the capital of Germany?",
        "role": "user"
      },
      {
        "content": "The capital of Germany is Berlin.",
        "role": "assistant"
      },
      {
        "content": user_input,
        "role": "user"
      }
    ],
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 800,
    "model": "comma-soft/comma-llm-l-v3",
    "knowledgebase_ids": knowledge_base_ids
  })

    response = requests.post(url, headers=headers, data=payload)

    return response

def create_chat(user_input):
    """
    Create a new chat session with initial conversation context.
    
    Args:
        user_input (str): Initial user message
        
    Returns:
        requests.Response: Response containing new chat session details
        
    Note:
        Includes predefined conversation context about Germany's capital
    """
    url = "https://app.alan.de/api/v1/chats/"

    #Configure the chat
    payload = json.dumps({
      "content": user_input,
      "settings": {
          "initial_conversation": [
                          {
                              "role": "user",
      "content": "What is the capital of Germany?"

                          },
                          {
                              "role": "assistant",
      "content": "The capital of Germany is Berlin."
                          },
          {
            "role": "user",
            "content": "Thank you!"
          },
          {
            "role": "assistant",
            "content": "You're welcome!"
          }
          ],
          "user_system_prompt": "",
          "knowledgebase_ids": knowledge_base_ids,
          "icon": "general",
          "model": "comma-soft/comma-llm-l-v3",
          "temperature": 0.7,
          "top_p": 0.95,
          "initial_message": "Hallo, ich bin Alan, Ihr persönlicher Assistent, und bin hier, um Ihnen beim Zusammenfassen, Übersetzen und Erstellen relevanter Texte für unsere Wissensdatenbank zu helfen."
        }
    })

    response = requests.post(url, headers=headers, data=payload)
    return response

def continue_chat(user_input, chat_id, previous_message_id):
    """
    Continue an existing chat conversation.
    
    Args:
        user_input (str): New user message
        chat_id (str): ID of the existing chat session
        previous_message_id (str): ID of the last message in conversation
        
    Returns:
        requests.Response: Response containing the AI's reply
        
    Note:
        Returns None if chat_id or previous_message_id is None
    """
    if(chat_id is not  None and previous_message_id is not None):
        url = f"https://app.alan.de/api/v1alpha/chats/{chat_id}/generate"

        payload = json.dumps({
          "previous_message_id": previous_message_id,
          "content": user_input
        })

        response = requests.post(url, headers=headers, data=payload)

        return response

# Load previous state
def load_state():
    """
    Load previous chat state from file.
    
    Returns:
        dict: Contains chat_id, previous_message_id, and knowledge_base_ids
        
    Note:
        Returns default state if file doesn't exist or is invalid
    """
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"chat_id": None, "previous_message_id": None, "knowledge_base_ids": knowledge_base_ids}

# Save state
def save_state(chat_id, previous_message_id):
    """
    Save current chat state to file.
    
    Args:
        chat_id (str): Current chat session ID
        previous_message_id (str): ID of last message
        
    Note:
        Saves to STATE_FILE in JSON format
    """
    with open(STATE_FILE, "w") as f:
        json.dump({"chat_id": chat_id, "previous_message_id": previous_message_id, "knowledge_base_ids": knowledge_base_ids}, f)

def get_file_path():
    """
    Get paths of all JSONL files in new_articles folder.
    
    Returns:
        list: Full paths of all .jsonl files in new_articles directory
    """
    folder="new_articles"
    return [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith(".jsonl")]

def get_file_id_from_knowledgebase(connector_id, knowledge_base_id):
    """
    Retrieve file IDs from a specific knowledge base.
    
    Args:
        connector_id (str): ID of the connector
        knowledge_base_id (str): ID of the knowledge base
        
    Returns:
        list: List of file IDs in the knowledge base
        
    Note:
        Returns empty list if no files found or on error
    """
    url = f"https://app.alan.de/api/v1alpha/connectors/{connector_id}/knowledge-bases/{knowledge_base_id}"
    response = requests.get(url, headers=headers)
    response = response.json()
    try:
        # Check if settings and files exist in the response
        if "settings" in response and "files" in response["settings"]:
            files = response["settings"]["files"]
            print(f"Found {len(files)} files in knowledge base")
            return files
        else:
            print("No files found in response")
            return []
            
    except Exception as e:
        print(f"Error extracting files: {str(e)}")
        return []
    
# Getting the file id and name
def get_file_id_and_name():
    """
    Get mapping of file IDs to file names for all uploaded files.
    
    Returns:
        list: List of dicts containing file_id and file_name
        
    Note:
        Saves results to file_info.json
    """
    response = get_uploaded_files()
    response = response.json()

    print(type(response))
    #print(response)

    if isinstance(response, dict) and "files" in response:
        json_files = response["files"]
        # Create list of dictionaries with file_id and file_name
        file_info = [{"file_id": file["resource_id"], "file_name": file["title"]} for file in json_files]
        
        # Write to JSON file
        with open('file_info.json', 'w') as f:
            json.dump(file_info, f, indent=2)

        return file_info
    else:
        print("Error: Response does not contain a 'files' list.")

# Getting file ids of the articles from articles.json and create a knowledge base
def create_knowledgebase_from_files(connector_id):
    """
    Create multiple knowledge bases from uploaded files.
    
    Args:
        connector_id (str): ID of the connector
        
    Returns:
        list: IDs of created knowledge bases
        
    Note:
        Splits files into three parts and creates separate knowledge base for each
    """
    """for file_name in files:
      response = upload_file(file_name)

      file_id = response.json().get("resource_id")
      _files.append(file_id)"""
    try:
        # Get all file info
        file_info = get_file_id_and_name()
        if not file_info:
            raise ValueError("No files found")

        # Calculate size of each part
        total_files = len(file_info)
        part_size = total_files // 3
        print(f"Total files: {total_files}, Files per part: {part_size}")

        # Split files into three parts
        parts = [
            file_info[i:i + part_size] 
            for i in range(0, total_files, part_size)
        ]

        # Create knowledge base for each part
        for index, part in enumerate(parts, 1):
            _files = [file["file_id"] for file in part]
            
            response = create_knowledge_base(connector_id, _files)
            
            if response.status_code == 200:
                knowledge_base_id = response.json().get("resource_id")
                print(f"Created knowledge base {index} with {len(_files)} files: {response.status_code}, {knowledge_base_id}")
            else:
                print(f"Error creating knowledge base {index}: {response.status_code}, {response.text}")

        print("Created knowledge bases with IDs:", knowledge_base_ids)
        return knowledge_base_ids

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Create knowledge bases
"""created_ids = create_knowledgebase_from_files(connector_id)

if created_ids:
    # Update environment variable
    os.environ["KNOWLEDGE_BASE_IDS"] = ",".join(created_ids)
    print(f"Successfully created {len(created_ids)} knowledge bases")
else:
    print("Failed to create knowledge bases")"""

# Delete the knowledge bases
"""for knowledge_base_id in delete_kb:
  response = delete_knowledge_base(knowledge_base_id)
  print(response.status_code, response.text)"""

# Update knowledge base
def update_knowledge_base(connector_id):
  """
    Update knowledge base with new articles.
    
    Args:
        connector_id (str): ID of the connector
        
    Returns:
        str: Status message with timestamp
        
    Note:
        Fetches new WordPress posts and updates knowledge base
        Returns different messages based on whether files existed or were updated
    """
  knowledge_base_id="9d25af80-7f0a-4488-a439-e192a36cdcb5"
  index = 1        
  url = f"https://app.alan.de/api/v1alpha/connectors/{connector_id}/knowledge-bases/{knowledge_base_id}"
  
  try:
    while True:
      files = []
      # Fetch posts from WordPress website and save them to a JSON file
      fetch_wordpress_posts(index)
      index += 1
        
  except Exception as e:
    if "File already exists" in str(e):
       return f"Wissensdatenbank aktuell. Zuletzt aktualisiert am:{datetime.datetime.now()}" 
    else:
      #get filenames from new_articles folder
      files = get_file_path()
      print(f"Printing the total number of files here: {len(files)}")
      files_in_knowledgebase = get_file_id_from_knowledgebase(connector_id, knowledge_base_id)
      for file_name in files:
        print(f"Uploading file: {file_name}")
        # Upload the file to CommaSoft
        response = upload_file(file_name)

        file_id = response.json().get("resource_id")
        files_in_knowledgebase.append(file_id)
        print(f"Uploaded file: {file_name} with ID: {file_id}")
        payload = json.dumps({
            "title": "Pfefferminzia Artikeln",
            "description": "Pfefferminzia Artikeln",
            "settings": {
              "kind": "file",
              "files": files_in_knowledgebase
            }
        })
        
        response = requests.put(url, headers=headers, data=payload)
        if response.status_code == 200:
          print(f"Updated knowledge base with {file_name}")
          file_info = [{"file_id": file_id, "file_name": file_name}]
          # Read existing data
          try:
            with open('file_info.json', 'r') as f:
              existing_data = json.load(f)
          except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []
          
          # Append new data
          existing_data.extend(file_info)
          
          # Write back to file
          with open('file_info.json', 'w') as f:
            json.dump(existing_data, f, indent=2)
      
        else:
          print(f"Error updating knowledge base with {file_name}: {response.status_code}, {response.text}")
          break
      print(f"Error: {str(e)}")
      return f"Wissendatenbank erfolgreich aktualisiert. Zuletzt aktualisiert am:{datetime.datetime.now()}"

# Delete the uploaded files
"""for file in resource_ids:
  response = requests.delete(f"https://app.alan.de/api/v1/files/{file}", headers=headers)
  print(response.status_code, response.text)"""

# Get the list of knowledge bases
response = requests.get("https://app.alan.de/api/v1/connectors/knowledge-bases", headers=headers)
response = response.json()

if isinstance(response, dict) and "knowledge_bases" in response:
    json_files = response["knowledge_bases"]
    resource_ids = [file["resource_id"] for file in json_files]
    print(f"Printing the size of the list here: {len(resource_ids)}.")
    os.environ["KNOWLEDGE_BASE_IDS"] = ",".join(resource_ids)
    knowledge_base_ids = resource_ids
    print(knowledge_base_ids)
else:
    print("Error: Response does not contain a 'files' list.")

# Querying the knowledge bases
"""flag = 0
for resource_id in resource_ids:
    if flag < 5:
      knowledge_base_ids.append(resource_id)
      flag += 1
answer = generate_response(knowledge_base_ids)
print(f"{answer.status_code}, and the answer: {answer.text}")"""

# Creating a chat
"""response = create_chat("Was ist haftplichtversicherung?")
print(response.status_code)

chat_id, message_id, message_content = extract_required_info(response.text)

# Print results
print("Chat ID:", chat_id)
os.environ["CHAT_ID"] = str(chat_id)
print("Message ID:", message_id)
os.environ["PREVIOUS_MESSAGE_ID"] = str(message_id)
print("Message Content:", message_content)"""

# Continue the chat
"""response = continue_chat("Was sind die anderen versicherungen und was ist die unterschied?", chat_id, str(message_id))
print(response.status_code)
chat_id, message_id, message_content = extract_required_info(response.text)

# Print results
print("Chat ID:", chat_id)
os.environ["CHAT_ID"] = str(chat_id)
print("Message ID:", message_id)
os.environ["PREVIOUS_MESSAGE_ID"] = str(message_id)
print("Message Content:", message_content)"""
