import json
import re
import os

def create_filename_from_title(json_data):
    title = json_data.get("title")
    filename = re.sub(r'\W+', '_', title)  # Replace non-word characters with underscores
    return f"{filename}.jsonl"

# Create articles directory if it doesn't exist
articles_dir = "articles"
if not os.path.exists(articles_dir):
    os.makedirs(articles_dir)
    
# Read JSON data from file
with open("articles.json", "r", encoding="utf-8") as file:
    json_objects = json.load(file)  # Assuming it's a list of JSON objects

# Generate filenames for each JSON object
filenames = []  # List to store filenames

for index, obj in enumerate(json_objects):  # Assuming json_objects is a list of JSON objects
    filename = create_filename_from_title(obj)  # Generate filename
    filepath = os.path.join(articles_dir, filename)  # Create full file path
    filenames.append(filepath)  # Store filepath in the list

    # Write JSON object to its corresponding JSONL file in the articles directory
    with open(filepath, "w", encoding="utf-8") as outfile:
        json.dump(obj, outfile, ensure_ascii=False)
        outfile.write("\n")  # JSONL format requires newline separation

    #print(f"Object {index + 1}: {filename}")