import requests
import json
import time
from categorize_articles import categorize_articles
from create import process_articles

# Base URL
BASE_URL = "https://pfefferminzia.de/wp-json/wp/v2/posts"
PER_PAGE = 100  # Max articles per request

all_articles = []
page = 1

# Fetch all articles dynamically
while True:
    url = f"{BASE_URL}?per_page={PER_PAGE}&page={page}"
    print(f"Fetching page {page}...")

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        #Create an empty list to append the required fields
        
        for post in data:
            all_articles.append({
                "title": post['title']['rendered'],
                "content": post['content']['rendered'],
                "date": post['date'],
                "category": post['class_list'],
                "author": post['yoast_head_json']['twitter_misc']['Geschrieben von']})            
        if not data:  # Stop if no more articles
            break
    else:
        print(f"Error fetching page {page}: {response.status_code}")
        break  # Stop fetching on error

    page += 1
    time.sleep(1)  # Prevent rate limits

# Ensure we have all articles
total_articles = len(all_articles)
print(f"Total articles fetched: {total_articles}")

# Split into 3 equal parts dynamically
split_size = total_articles // 3
json1, json2, json3 = all_articles[:split_size], all_articles[split_size:2*split_size], all_articles[2*split_size:]

# Save JSON files
with open("articles_part1.json", "w", encoding="utf-8") as f:
    json.dump(json1, f, indent=4, ensure_ascii=False)
categorize_articles("articles_part1.json", "articles_part1.json")
process_articles("articles_part1.json")

with open("articles_part2.json", "w", encoding="utf-8") as f:
    json.dump(json2, f, indent=4, ensure_ascii=False)
categorize_articles("articles_part2.json", "articles_part2.json")
process_articles("articles_part2.json")

with open("articles_part3.json", "w", encoding="utf-8") as f:
    json.dump(json3, f, indent=4, ensure_ascii=False)
categorize_articles("articles_part3.json", "articles_part3.json")
process_articles("articles_part3.json")

print("All JSON files saved successfully!")
