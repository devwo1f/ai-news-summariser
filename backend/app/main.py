from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from app.news_client import get_news
from app.models import extract_content, summarize_article
from app.schemas import NewsResponse, SummarizeRequest

app = FastAPI(title="AI News Summarizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI News Summarizer API."}

@app.get("/news/search", response_model=NewsResponse)
def search_news(q: str = "", language: str = "en", page: int = 1):
    """
    Step 1: Get Headlines ONLY (Fast).
    If 'q' is empty, returns Top Headlines.
    """
    # 20 Articles per page ensures the feed is long enough to scroll
    ARTICLES_PER_PAGE = 20 
    
    print(f"🔎 Fetching news (Query: '{q}', Page: {page}, Limit: {ARTICLES_PER_PAGE})")
    
    articles = get_news(
        query=q, 
        language=language, 
        page_size=ARTICLES_PER_PAGE, 
        page=page
    )
    return NewsResponse(total_results=len(articles), articles=articles)

@app.post("/news/summarize")
def summarize_news_article(request: SummarizeRequest):
    """
    Step 2: Summarize a single article (Slow/AI).
    """
    print(f"   🤖 Summarizing: {request.url}")
    
    full_text = extract_content(request.url)
    
    if full_text:
        summary = summarize_article(full_text)
        return {"summary": summary, "full_text": full_text[:200] + "..."}
    else:
        return {"summary": "Could not extract content (Protected or Dead Link).", "full_text": None}