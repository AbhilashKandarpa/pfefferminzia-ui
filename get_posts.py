import json
import requests
import tiktoken
import os
from categorize_articles import categorize_articles
from dotenv import load_dotenv

load_dotenv()

# load the OpenAI API KEY
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# Select the encoding
encoding = tiktoken.encoding_for_model("gpt-4")

# Set up the API endpoint and parameters
url = "https://pfefferminzia.de/wp-json/wp/v2/posts"
params = {
    "per_page": 100,  # Number of posts
    "page": 3        # Pagination
}

# Make the API request
response = requests.get(url, params=params)

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

    # Save the posts to a JSON file
    with open("wordpress_posts.json", "w", encoding="utf-8") as file:
        json.dump(formatted_posts, file, ensure_ascii=False, indent=4)
    
    categorize_articles("wordpress_posts.json", "articles.json")

    with open("articles.json", "r", encoding="utf-8") as file:
        json_string = file.read()

        print("Total number of tokens when encoded with gpt-4 are: ", len(encoding.encode(json_string)))

else:
    print(f"Error: {response.status_code} - {response.text}")