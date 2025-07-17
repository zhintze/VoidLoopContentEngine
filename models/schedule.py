from pydantic import BaseModel
from typing import List, Dict, Optional

class Schedule(BaseModel):
    days: List[str]
    time: str
    timezone: str
    max_post_per_day: int