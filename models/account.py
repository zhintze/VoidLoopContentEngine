from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from models.output import Output
from models.post import Post
from models.log_entry import LogEntry
from enum import Enum


class AccountStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class APICredentials(BaseModel):
    """API credentials for social media platforms"""
    instagram_access_token: Optional[str] = None
    instagram_page_id: Optional[str] = None
    pinterest_access_token: Optional[str] = None
    pinterest_board_name: str = "Recipes"
    default_image_url: Optional[str] = None


class Account(BaseModel):
    account_id: str
    name: str
    site: str
    social_handles: Dict[str, str] = Field(default_factory=dict)
    keywords: List[str]
    tone: str = "neutral"
    hashtags: List[str] = Field(default_factory=list)
    template_id: str
    api_credentials: APICredentials = Field(default_factory=APICredentials)
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
        data = self.dict(
            exclude={"outputs", "post_queue", "log_entries"}  # skip volatile content
        )
        with open(path, "w") as f:
            toml.dump(data, f)
    
    def has_instagram_credentials(self) -> bool:
        """Check if Instagram API credentials are configured"""
        return (self.api_credentials.instagram_access_token is not None and 
                self.api_credentials.instagram_page_id is not None)
    
    def has_pinterest_credentials(self) -> bool:
        """Check if Pinterest API credentials are configured"""
        return self.api_credentials.pinterest_access_token is not None

