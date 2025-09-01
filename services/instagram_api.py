import requests
import os
from typing import Optional, Dict, Any
import json


class InstagramAPI:
    """Instagram Graph API integration for Business/Creator accounts"""
    
    def __init__(self, access_token: str, page_id: str):
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v19.0"
        
    def create_media_container(self, image_url: str, caption: str) -> Optional[str]:
        """Create a media container for posting"""
        url = f"{self.base_url}/{self.page_id}/media"
        
        params = {
            'image_url': image_url,
            'caption': caption,
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('id')
        except requests.RequestException as e:
            print(f"Error creating media container: {e}")
            return None
    
    def publish_media(self, creation_id: str) -> bool:
        """Publish the media container"""
        url = f"{self.base_url}/{self.page_id}/media_publish"
        
        params = {
            'creation_id': creation_id,
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            data = response.json()
            print(f"Successfully published to Instagram: {data.get('id')}")
            return True
        except requests.RequestException as e:
            print(f"Error publishing media: {e}")
            return False
    
    def post_image(self, image_url: str, caption: str) -> bool:
        """Complete workflow: create container and publish"""
        print(f"Posting to Instagram: {caption[:50]}...")
        
        # Step 1: Create media container
        creation_id = self.create_media_container(image_url, caption)
        if not creation_id:
            return False
            
        # Step 2: Publish media
        return self.publish_media(creation_id)
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get Instagram account information"""
        url = f"{self.base_url}/{self.page_id}"
        
        params = {
            'fields': 'id,name,username,followers_count',
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting account info: {e}")
            return {}


class InstagramAPIConfig:
    """Configuration management for Instagram API"""
    
    @staticmethod
    def from_env() -> Optional[InstagramAPI]:
        """Create Instagram API instance from environment variables (legacy)"""
        access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        page_id = os.getenv('INSTAGRAM_PAGE_ID')
        
        if not access_token or not page_id:
            print("Missing Instagram API credentials in environment variables")
            print("Required: INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_PAGE_ID")
            return None
            
        return InstagramAPI(access_token, page_id)
    
    @staticmethod
    def from_account(account) -> Optional[InstagramAPI]:
        """Create Instagram API instance from account credentials"""
        credentials = account.api_credentials
        
        if not credentials.instagram_access_token or not credentials.instagram_page_id:
            return None
            
        return InstagramAPI(credentials.instagram_access_token, credentials.instagram_page_id)