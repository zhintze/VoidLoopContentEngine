from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from models.schedule import Schedule

class Template(BaseModel):
    id: str
    name: str
    description: str
    temperature: float
    model: str
    schedule: Schedule
    
    # Trend integration settings
    use_trends: Optional[bool] = True
    trend_preferences: Optional[Dict[str, Any]] = None
    max_trend_keywords: Optional[int] = 3
    platform_optimization: Optional[bool] = True