import json
import os
import create
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALAN_API_KEY")
headers = {"Authorization": f"Bearer {API_KEY}"}
connector_id="0b484b74-06e6-4e11-9389-a2088f12e99c"
knowledge_base_ids=[]
chat_id="cf33da44-d05a-4bdb-bc87-4b1ae4426648"

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

def create_chat():
    url = "https://app.alan.de/api/v1/chats/"

    #Configure the chat
    payload = json.dumps({
      "content": "Wie trägt die Digitalisierung zur Nachhaltigkeit in der Versicherungsbranche bei, und welche Rolle spielt dabei Cloud Computing?",
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

def continue_chat(chat_id):
    url = "https://app.alan.de/api/v1/chats/cf33da44-d05a-4bdb-bc87-4b1ae4426648/generate/"

    payload = json.dumps({
      "previous_message_id": "00ef3812-d9e4-48e5-bed7-d591b63612cb",
      "content": "Was ist die unterschied zwischen SPV und GKV? Welche versicherung ist billiger?"
    })

    response = requests.post(url, headers=headers, data=payload)

    return response

# Getting file ids of the first 100 articles from Pfefferminzia
for file_name in files:
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

print(knowledge_base_ids)

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
    print(type(response))
    json_files = response["knowledge_bases"]
    resource_ids = [file["resource_id"] for file in json_files]
    print(f"Printing the size of the list here: {len(resource_ids)}.")
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
"""response = create_chat()
print(response.status_code, response.text)"""

# Continue the chat
"""response = continue_chat(chat_id)
print(response.status_code, response.text)"""
