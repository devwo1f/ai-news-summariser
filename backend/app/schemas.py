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
    # We add a loading state flag for the frontend (optional in backend, but good practice)
    is_loading: Optional[bool] = False 

class NewsResponse(BaseModel):
    total_results: int
    articles: list[Article]

# New Request Model for Phase 4.5
class SummarizeRequest(BaseModel):
    url: str