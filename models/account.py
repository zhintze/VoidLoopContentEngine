from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from models.output import Output
from models.post import Post
from models.log_entry import LogEntry
from models.theme import ThemePreferences
from enum import Enum


class AccountStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class APICredentials(BaseModel):
    """API credentials for social media platforms"""
    # Instagram
    instagram_access_token: Optional[str] = None
    instagram_page_id: Optional[str] = None
    
    # Pinterest  
    pinterest_access_token: Optional[str] = None
    pinterest_board_name: str = "Recipes"
    
    # Facebook
    facebook_access_token: Optional[str] = None
    facebook_page_id: Optional[str] = None
    
    # Twitter/X
    twitter_bearer_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    
    # Shared
    default_image_url: Optional[str] = None


class Account(BaseModel):
    account_id: str
    name: str
    site: str
    social_handles: Dict[str, str] = Field(default_factory=dict)
    
    # Theme system integration
    theme_id: str = Field(default="food_recipe_general", description="ID of the theme to use for content generation")
    theme_preferences: ThemePreferences = Field(default_factory=ThemePreferences, description="User preferences for theme application")
    
    # Legacy keyword system (will be populated from theme)
    keywords: List[str] = Field(default_factory=list, description="Deprecated: Use theme system instead")
    tone: str = Field(default="friendly", description="Content tone - should match theme content_tones")
    hashtags: List[str] = Field(default_factory=list, description="Deprecated: Use theme system instead")
    
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
    
    def has_facebook_credentials(self) -> bool:
        """Check if Facebook API credentials are configured"""
        return (self.api_credentials.facebook_access_token is not None and 
                self.api_credentials.facebook_page_id is not None)
    
    def has_twitter_credentials(self) -> bool:
        """Check if Twitter API credentials are configured"""
        return self.api_credentials.twitter_bearer_token is not None
    
    def get_platform_status(self) -> Dict[str, bool]:
        """Get status of all platform credentials"""
        return {
            'instagram': self.has_instagram_credentials(),
            'pinterest': self.has_pinterest_credentials(),
            'facebook': self.has_facebook_credentials(),
            'twitter': self.has_twitter_credentials()
        }
    
    def get_theme_keywords(self, platform: str = None) -> List[str]:
        """Get keywords from theme system (replaces legacy keywords)"""
        from services.theme_loader import theme_loader
        
        if not self.theme_preferences.primary_categories:
            # If no preferences set, use all categories from theme
            theme_data = theme_loader.apply_theme_preferences(self.theme_id, self.theme_preferences)
            return theme_data.get("keywords", [])
        
        # Apply preferences to get filtered keywords
        theme_data = theme_loader.apply_theme_preferences(self.theme_id, self.theme_preferences)
        keywords = theme_data.get("keywords", [])
        
        # Add platform-specific keywords if requested
        if platform:
            for category in self.theme_preferences.primary_categories:
                platform_keywords = theme_loader.get_keywords_for_category(
                    self.theme_id, category, platform
                )
                keywords.extend(platform_keywords)
        
        # Remove duplicates
        return list(set(keywords))
    
    def get_theme_hashtags(self, platform: str) -> List[str]:
        """Get hashtags from theme system for specific platform"""
        from services.theme_loader import theme_loader
        
        hashtags = theme_loader.get_platform_hashtags(
            self.theme_id, 
            platform, 
            self.theme_preferences.primary_categories or None
        )
        
        return hashtags
    
    def get_content_tone_guidance(self) -> Dict[str, List[str]]:
        """Get content tone keywords and guidance from theme"""
        from services.theme_loader import theme_loader
        
        return theme_loader.get_content_tone_keywords(self.theme_id, self.tone)
    
    def get_engagement_elements(self) -> Dict[str, List[str]]:
        """Get call-to-actions and engagement phrases from theme"""
        from services.theme_loader import theme_loader
        
        return theme_loader.get_engagement_elements(self.theme_id)
    
    def update_theme_preferences(self, **preferences):
        """Update theme preferences"""
        for key, value in preferences.items():
            if hasattr(self.theme_preferences, key):
                setattr(self.theme_preferences, key, value)
    
    def switch_theme(self, new_theme_id: str):
        """Switch to a different theme"""
        from services.theme_loader import theme_loader
        
        if theme_loader.get_theme(new_theme_id):
            self.theme_id = new_theme_id
            # Reset preferences to defaults for new theme
            self.theme_preferences = ThemePreferences()
        else:
            raise ValueError(f"Theme '{new_theme_id}' not found")
    
    def get_dietary_keywords(self, restriction: str) -> Dict[str, List[str]]:
        """Get keywords for a specific dietary restriction"""
        from services.theme_loader import theme_loader
        
        return theme_loader.get_dietary_restriction_keywords(self.theme_id, restriction)

