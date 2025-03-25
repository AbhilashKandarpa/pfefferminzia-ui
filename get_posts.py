import json
import requests
from categorize_articles import categorize_articles
from create import create_filename_from_title, process_articles

def file_name_exists(json_file_path, new_file_name):
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)  # Load JSON data (expects a list of dictionaries)
        
        # Create a set of existing file names for quick lookup
        file_names = {entry["file_name"] for entry in data}

        return new_file_name in file_names  # Fast O(1) lookup
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print("Error reading JSON file:", e)
        return False  # Assume file_name doesn't exist if error occurs

def fetch_wordpress_posts(page_number):
    # Set up the API endpoint and parameters
    url = "https://pfefferminzia.de/wp-json/wp/v2/posts"
    params = {
        "per_page": 1,  # Number of posts
        "page": page_number          # Pagination
    }    
    # Make the API request
    response = requests.get(url, params=params)
    process_wordpress_response(response)

def process_wordpress_response(response):
    if response.status_code == 200:
        posts = response.json()

        #Create an empty list to append the required fields
        formatted_posts = []

        for post in posts:
            formatted_posts.append({
                "title": post['title']['rendered'],
                "content": post['content']['rendered'],
                "date": post['date'],
                "category": post['class_list'],
                "author": post['yoast_head_json']['twitter_misc']['Geschrieben von']})
            
        # Check if the file already exists in the knowledgebase
        for post in formatted_posts:
            filename = create_filename_from_title(post)
            print(f"Checking if file '{filename}' already exists in the knowledge base...")
            # Check if the file exists in the knowledge base
            file_exists = file_name_exists("file_info.json", f"new_articles\\{filename}")
            # If it does, skip the processing step
            if file_exists:
                print(f"File '{filename}' already exists in the knowledge base. Skipping processing...")
                raise Exception("File already exists")
            else:
                print(f"File '{filename}' does not exist in the knowledge base. Proceeding with processing...")
            
        # Save the posts to a JSON file
        with open("articles_part4.json", "w", encoding="utf-8") as file:
            json.dump(formatted_posts, file, ensure_ascii=False, indent=4)
        
        categorize_articles("articles_part4.json", "articles_part4.json")
        process_articles("articles_part4.json")

    else:
        print(f"Error: {response.status_code} - {response.text}")
