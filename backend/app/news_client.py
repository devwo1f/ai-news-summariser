import requests
from app.schemas import Article, NewsResponse

# --- DEBUG PRINT ---
# If you don't see this line in your terminal, 
# you are running an old version of the file!
print("DEBUG: Loaded the HARDCODED version of news_client.py")
# -------------------

# --- HARDCODED CONFIGURATION ---
NEWS_API_KEY = "c2117d778ff6448886214ed9c4c614f3"
BASE_URL = "https://newsapi.org/v2/everything"

def get_news(query: str, language: str = "en", page_size: int = 5) -> list[Article]:
    """
    Fetches news articles from NewsAPI based on a query.
    Returns a list of Article objects (defined in schemas.py).
    """
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": language,
        "pageSize": page_size,
        "sortBy": "relevancy"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() 
        
        data = response.json()
        
        if data.get("status") != "ok":
            print(f"API Error: {data.get('message')}")
            return []

        articles = []
        for item in data.get("articles", []):
            source_data = item.get("source") or {}
            
            article = Article(
                title=item.get("title") or "No Title",
                description=item.get("description"),
                url=item.get("url"),
                source_name=source_data.get("name", "Unknown Source"),
                image_url=item.get("urlToImage")
            )
            articles.append(article)
            
        return articles

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []