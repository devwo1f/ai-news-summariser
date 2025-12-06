from pydantic import BaseModel
from typing import Optional

class Article(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    source_name: str
    image_url: Optional[str] = None
    full_text: Optional[str] = None
    summary: Optional[str] = None
    # We add a loading state flag for the frontend 
    is_loading: Optional[bool] = False 

class NewsResponse(BaseModel):
    total_results: int
    articles: list[Article]

# --- THE MISSING CLASS ---
class SummarizeRequest(BaseModel):
    url: str