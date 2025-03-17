from googlesearch import search

def fetch_article_url(article_name):
    query = f"site:pfefferminzia.de {article_name}"  # Search only within pfefferminzia.de
    try:
        # Get the first search result
        article_url = next(search(query, num=1, stop=1, pause=2))  
        return f'<a href="{article_url}">{article_name}</a>'
    except StopIteration:
        return f"No results found for {article_name}."
    except Exception as e:
        return f"An error occurred: {str(e)}"
