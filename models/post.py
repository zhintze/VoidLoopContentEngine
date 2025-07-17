from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Post(BaseModel):
    post_id: str
    markdown: str
    date_generated: datetime
    date_posted: Optional[datetime] = None
    platforms_posted: List[str]
    image_url: Optional[str] = None
    alt_text: Optional[str] = None