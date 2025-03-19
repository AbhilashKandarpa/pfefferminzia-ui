import json
import os
import create
import requests
from extract_chat_info import extract_required_info
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

#get filenames from create.py
files = create.filenames
_files = []
def upload_file(file_name):
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

def get_file_id():
    url = "https://app.alan.de/api/v1/files/"
    
    response = requests.get(url, headers=headers)

    return response

def create_knowledge_base(connector_id, file_name, _files):
    url = f"https://app.alan.de/api/v1/connectors/{connector_id}/knowledge-bases"

    payload = json.dumps({
        "title": file_name,
        "description": file_name,
        "settings": {
          "kind": "file",
          "files": _files
        }
    })

    response = requests.post(url, headers=headers, data=payload)

    return response

def delete_knowledge_base(knowledge_base_id):
    url = f"https://app.alan.de/api/v1/connectors/{connector_id}/knowledge-bases/{knowledge_base_id}"

    response = requests.delete(url, headers=headers)

    return response

def generate_response(user_input):
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
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"chat_id": None, "previous_message_id": None}

# Save state
def save_state(chat_id, previous_message_id):
    with open(STATE_FILE, "w") as f:
        json.dump({"chat_id": chat_id, "previous_message_id": previous_message_id}, f)


# Getting file ids of the first 100 articles from Pfefferminzia
"""for file_name in files:
  response = upload_file(file_name)

  file_id = response.json().get("resource_id")
  _files.append(file_id)
  #print(response.status_code, file_id)

# Creating a knowledge base with the first 100 articles from Pfefferminzia
try:
  response = create_knowledge_base(connector_id, file_name, _files)
  #print(response.status_code, response.text)
  knowledge_base_id = response.json().get("resource_id")
  knowledge_base_ids.append(knowledge_base_id)
  print(response.status_code, knowledge_base_id)
except Exception as e:
  print("Error: ", response.status_code, response.text)  

print(knowledge_base_ids)"""

# Getting the file id
"""file_ids = []
response = get_file_id()
response = response.json()

print(type(response))
print(response)

if isinstance(response, dict) and "files" in response:
    json_files = response["files"]
    resource_ids = [file["resource_id"] for file in json_files]
    print(f"Printng the size of the list here: {len(resource_ids)}. \nAnd the actual list here: {resource_ids}")
else:
    print("Error: Response does not contain a 'files' list.")"""

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

# Delete the knowledge bases
"""for knowledge_base_id in knowledge_base_ids:
  response = delete_knowledge_base(knowledge_base_id)
  print(response.status_code, response.text)"""

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
