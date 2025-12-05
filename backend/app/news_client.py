import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from app.schemas import Article, NewsResponse

# --- ROBUST ENV LOADING ---
# 1. Calculate the exact path to backend/.env based on THIS file's location
#    Structure: backend/app/news_client.py
#    We want:   backend/.env
current_file_path = Path(__file__).resolve()
env_path = current_file_path.parent.parent / '.env'

# 2. Try to load it
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Fallback: Just try loading from the current directory
    load_dotenv()
# ----------------

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

def get_news(query: str, language: str = "en", page_size: int = 5) -> list[Article]:
    """
    Fetches news articles from NewsAPI based on a query.
    Returns a list of Article objects (defined in schemas.py).
    """
    # --- DEBUGGING BLOCK ---
    if not NEWS_API_KEY:
        print("\n" + "!"*60)
        print("❌ CRITICAL ERROR: NEWS_API_KEY is missing.")
        print("-" * 60)
        print(f"1. I looked for the .env file here:\n   {env_path}")
        print(f"2. Does this file exist? -> {env_path.exists()}")
        print(f"3. Current Working Directory: {os.getcwd()}")
        print("-" * 60)
        print("FIX: Check that 'backend/.env' exists and has no extra extension (like .txt)")
        print("!"*60 + "\n")
        raise ValueError("API Key not found. See debug info above.")
    # -----------------------

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