import requests
import os
from dotenv import load_dotenv
from app.schemas import Article, NewsResponse

# Load environment variables from .env file
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

def get_news(query: str, language: str = "en", page_size: int = 5) -> list[Article]:
    """
    Fetches news articles from NewsAPI based on a query.
    Returns a list of Article objects (defined in schemas.py).
    """
    if not NEWS_API_KEY:
        raise ValueError("NEWS_API_KEY is not set in the environment variables.")

    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": language,
        "pageSize": page_size,
        "sortBy": "relevancy"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() # Raise an error for 4xx or 5xx status codes
        
        data = response.json()
        
        if data.get("status") != "ok":
            print(f"API Error: {data.get('message')}")
            return []

        # Convert raw JSON into our nice Pydantic models
        articles = []
        for item in data.get("articles", []):
            # Handle cases where source might be None
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