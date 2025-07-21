from pydantic import BaseModel
from typing import Dict, Any
from models.schedule import Schedule

class Template(BaseModel):
    id: str
    name: str
    description: str
    temperature: float
    model: str
    #output_targets: str
    #prompt_structure: Dict[str, str]
    #content_layout: Dict[str, Any]
    schedule: Schedule