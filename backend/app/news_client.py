import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from app.schemas import Article, NewsResponse

# --- ROBUST ENV LOADING ---
current_file_path = Path(__file__).resolve()
env_path = current_file_path.parent.parent / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()
# ----------------

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# We now toggle between two endpoints
ENDPOINT_EVERYTHING = "https://newsapi.org/v2/everything"
ENDPOINT_HEADLINES = "https://newsapi.org/v2/top-headlines"

def get_news(query: str = "", language: str = "en", page_size: int = 10, page: int = 1) -> list[Article]:
    """
    Fetches news. If query is empty, fetches Top Headlines.
    """
    if not NEWS_API_KEY:
        raise ValueError("NEWS_API_KEY is not set. Check your .env file.")

    if query:
        # User is searching for something specific
        url = ENDPOINT_EVERYTHING
        params = {
            "q": query,
            "apiKey": NEWS_API_KEY,
            "language": language,
            "pageSize": page_size,
            "sortBy": "relevancy",
            "page": page
        }
    else:
        # User wants the "Front Page" (Top Headlines)
        url = ENDPOINT_HEADLINES
        params = {
            "country": "us", # Default to US for general feed
            "apiKey": NEWS_API_KEY,
            "pageSize": page_size,
            "page": page
        }

    try:
        response = requests.get(url, params=params)
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