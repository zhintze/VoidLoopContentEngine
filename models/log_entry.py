from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class LogType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    ACTION = "action"


class LogEntry(BaseModel):
    id: str
    account_id: str
    timestamp: datetime
    message: str
    type: LogType = LogType.INFO
    related_output_id: str | None = None
