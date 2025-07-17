from pydantic import BaseModel
from typing import List
from models.output import Output
from models.post import Post
from models.log_entry import LogEntry
from enum import Enum


class AccountStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class Account(BaseModel):
    account_id: str
    name: str
    template_id: str
    outputs: List[Output]
    keywords: List[str]
    status: AccountStatus
    post_queue: List[Post]
    log_entries: List[LogEntry]

    def create_account(self):
        ...

    def delete_account(self):
        ...

    def pause_account(self):
        self.status = AccountStatus.PAUSED

    def resume_account(self):
        self.status = AccountStatus.ACTIVE