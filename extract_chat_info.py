import json
import re

def clean_json(response_text, max_attempts=3):
    """
    Cleans and fixes JSON formatting issues from streaming responses.

    Args:
        response_text (str): The malformed JSON string
        max_attempts (int): Maximum number of cleaning attempts

    Returns:
        str: A cleaned JSON string or None if cleaning fails
    """
    if max_attempts <= 0:
        print("Maximum cleaning attempts reached")
        return None
        
    try:
        # Basic string cleanup
        response_text = response_text.strip()
        
        # Handle incomplete JSON objects
        if not response_text.endswith('}'):
            response_text += '}'
            
        # Fix missing commas between arrays and objects
        response_text = re.sub(r'}\s*{', '},{', response_text)
        
        # Fix incomplete content arrays
        if '"content":' in response_text and not response_text.endswith(']}'):
            response_text = re.sub(r'"content":\s*"([^"]*)"?(?=\s*[,}])', r'"content":"\1"', response_text)
        
        # Fix unquoted values
        response_text = re.sub(r':\s*([\w.-]+)([,}])', r':"\1"\2', response_text)
        
        # Fix missing quotes around keys
        response_text = re.sub(r'([{,])\s*(\w+):', r'\1"\2":', response_text)
        
        # Ensure proper JSON structure
        try:
            parsed = json.loads(response_text)
            return json.dumps(parsed)  # Reformat to ensure valid JSON
        except json.JSONDecodeError:
            # If parsing fails, try one more cleanup pass
            return clean_json(response_text, max_attempts - 1)
            
    except Exception as e:
        print(f"Warning: Could not clean JSON (attempt {4-max_attempts}/3): {str(e)}")
        return None

# Add this helper function to validate individual tokens
def is_valid_json(json_str):
    """
    Validates if a string is valid JSON.
    
    Args:
        json_str (str): JSON string to validate
    
    Returns:
        bool: True if valid JSON, False otherwise
    """
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False

def extract_required_info(response_text):
    """
    Extracts chat_id, message_id, and assistant message content from streaming responses.
    
    Args:
        response_text (str): The complete response text containing JSON objects
        
    Returns:
        tuple: (chat_id, message_id, message_content)
    """
    generating_state = None
    assistant_message = None
    tokens = []
    
    # Extract JSON objects from the streamed response
    matches = re.findall(r'data:\s*(.*?)(?=data:|$)', response_text, re.DOTALL)
    
    for json_str in matches:
        json_str = json_str.strip()
        if not json_str:
            continue
            
        try:
            if not is_valid_json(json_str):
                json_str = clean_json(json_str)
                if not json_str:
                    continue
                    
            obj = json.loads(json_str)
            
            # Handle different types of messages
            if obj.get("kind") == "state" and obj.get("state") == "Generating":
                generating_state = obj
            elif obj.get("kind") == "tokens":
                tokens.append(obj.get("tokens", ""))
            elif obj.get("kind") == "message" and obj.get("message", {}).get("role") == "assistant":
                assistant_message = obj
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            continue
    
    # Extract required information
    chat_id = generating_state.get("chat_id") if generating_state else None
    message_id = generating_state.get("message_id") if generating_state else None
    
    # Combine tokens if no complete message is available
    message_content = None
    if assistant_message:
        message_content = assistant_message.get("message", {}).get("content")
    elif tokens:
        message_content = "".join(tokens)
    
    return chat_id, message_id, message_content