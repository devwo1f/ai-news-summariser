from pydantic import BaseModel
from typing import Optional

class Article(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    source_name: str
    image_url: Optional[str] = None
    # We will populate this in Phase 3
    full_text: Optional[str] = None
    summary: Optional[str] = None

class NewsResponse(BaseModel):
    total_results: int
    articles: list[Article]