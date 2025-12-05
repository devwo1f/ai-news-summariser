from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.news_client import get_news
from app.models import extract_content, summarize_article
from app.schemas import NewsResponse

app = FastAPI(title="AI News Summarizer")

# Enable CORS (Cross-Origin Resource Sharing)
# This allows your React Frontend (running on a different port) to talk to this Backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI News Summarizer API. Go to /docs to test it!"}

@app.get("/news/search", response_model=NewsResponse)
def search_news(q: str, language: str = "en"):
    """
    Search for news, scrape the content, and summarize the top articles.
    """
    print(f"🔎 Received search query: {q}")
    
    # 1. Fetch relevant articles from NewsAPI
    articles = get_news(query=q, language=language, page_size=5)
    
    if not articles:
        return NewsResponse(total_results=0, articles=[])

    # 2. Summarize only the top 2 articles to keep response time reasonable
    # (Scraping and summarizing takes time!)
    for i in range(min(2, len(articles))):
        article = articles[i]
        print(f"   📝 Summarizing article: {article.title[:30]}...")
        
        # Scrape full text
        full_text = extract_content(article.url)
        
        if full_text:
            # Generate AI Summary
            article.summary = summarize_article(full_text)
            article.full_text = full_text[:200] + "..." # Store just a snippet for debugging
        else:
            article.summary = "Could not scrape content (likely blocked or paywalled)."

    return NewsResponse(total_results=len(articles), articles=articles)