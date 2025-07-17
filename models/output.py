from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class OutputStatus(str, Enum):
    QUEUED = "queued"
    GENERATED = "generated"
    APPROVED = "approved"
    FAILED = "failed"



class Output(BaseModel):
    output_id: str
    account_id: str
    template_id: str
    status: OutputStatus
    generated_content: Dict[str, str]
    date_generated: datetime
    date_approved: Optional[datetime] = None
    errors: List[str] = []
    admin_notes: Optional[str] = None

    def generate(self):
        ...