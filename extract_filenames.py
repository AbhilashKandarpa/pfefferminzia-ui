import re

def extract_document_names(text):
    # Regular expression to match file names with .jsonl extension
    pattern = r'[-\s]?(?:articles\\)?([\wäöüßÄÖÜ\-]+)\.jsonl'
    
    # Find all matches and clean up the names
    matches = re.findall(pattern, text)

    # Process: Remove underscores and return clean names
    clean_names = [match.replace("_", " ") for match in matches]

    return clean_names
