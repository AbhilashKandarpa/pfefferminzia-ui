import json

def categorize_articles(input_file, output_file):
    """
    Reads a JSON file, categorizes articles based on predefined categories, 
    and writes the updated data to a new JSON file.
    """
    # Define allowed categories
    allowed_categories = {
        "arbeit", "gesundheit", "mobilitaet", "gewerbe",
        "vertrieb", "vorsorge", "zuhause", "branche"
    }

    # Load the JSON file
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Process each entry
    for article in data:
        categories = article.get("category", [])

        # Find the first matching category from allowed_categories
        matched_category = next(
            (cat.replace("category-", "") for cat in categories if cat.startswith("category-") and cat.replace("category-", "") in allowed_categories),
            None
        )

        # Check if any category starts with "im_fokus"
        if not matched_category and any(cat.startswith("im_fokus") for cat in categories):
            matched_category = "im fokus"
        
        # Check if the article should be categorized as "advertorial"
        elif not matched_category and "category-advertorial" in categories:
            matched_category = "advertorial"

        # Update the category field
        article["category"] = matched_category if matched_category else "uncategorized"

    # Save the modified JSON file
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"JSON file updated successfully! Output saved to {output_file}")
