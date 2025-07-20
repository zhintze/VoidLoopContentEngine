from pydantic import BaseModel, Field
from typing import List, Dict
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
    site: str
    social_handles: Dict[str, str] = Field(default_factory=dict)
    keywords: List[str]
    tone: str = "neutral"
    hashtags: List[str] = Field(default_factory=list)
    template_id: str
    outputs: List[Output] = Field(default_factory=list)
    status: AccountStatus = AccountStatus.ACTIVE
    post_queue: List[Post] = Field(default_factory=list)
    log_entries: List[LogEntry] = Field(default_factory=list)

    def create_account(self, **kwargs):
        # Optional placeholder for validation/init logic
        return Account(**kwargs)

    def delete_account(self):
        # Implement deletion logic (e.g. remove from storage)
        ...

    def pause_account(self):
        self.status = AccountStatus.PAUSED

    def resume_account(self):
        self.status = AccountStatus.ACTIVE

    @classmethod
    def from_toml(cls, path: str) -> "Account":
        import toml
        data = toml.load(path)
        return cls(**data)

    def save_to_toml(self, path: str):
        import toml
        with open(path, "w") as f:
            toml.dump(self.dict(), f)

