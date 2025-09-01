import requests
import os
from typing import Optional, Dict, Any
import json


class FacebookAPI:
    """Facebook Pages API integration for posting to Facebook Pages"""
    
    def __init__(self, access_token: str, page_id: str):
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v19.0"
        
    def get_page_info(self) -> Dict[str, Any]:
        """Get Facebook page information"""
        url = f"{self.base_url}/{self.page_id}"
        
        params = {
            'fields': 'id,name,username,followers_count,fan_count',
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting page info: {e}")
            return {}
    
    def create_post(self, message: str, link: Optional[str] = None, 
                    image_url: Optional[str] = None) -> bool:
        """Create a new post on the Facebook Page"""
        url = f"{self.base_url}/{self.page_id}/feed"
        
        data = {
            'message': message,
            'access_token': self.access_token
        }
        
        if link:
            data['link'] = link
            
        if image_url:
            # For images, we need to use a different approach
            return self.create_photo_post(message, image_url, link)
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            print(f"Successfully posted to Facebook: {result.get('id')}")
            return True
        except requests.RequestException as e:
            print(f"Error creating post: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return False
    
    def create_photo_post(self, message: str, image_url: str, 
                         link: Optional[str] = None) -> bool:
        """Create a photo post on the Facebook Page"""
        url = f"{self.base_url}/{self.page_id}/photos"
        
        data = {
            'url': image_url,
            'caption': message,
            'access_token': self.access_token
        }
        
        if link:
            data['link'] = link
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            print(f"Successfully posted photo to Facebook: {result.get('id')}")
            return True
        except requests.RequestException as e:
            print(f"Error creating photo post: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return False
    
    def post_content(self, message: str, image_url: Optional[str] = None, 
                     link: Optional[str] = None) -> bool:
        """Complete workflow: create and post content"""
        print(f"Posting to Facebook: {message[:50]}...")
        
        if image_url:
            return self.create_photo_post(message, image_url, link)
        else:
            return self.create_post(message, link, image_url)
    
    def get_page_access_token(self, user_access_token: str) -> Optional[str]:
        """Get a page access token from a user access token"""
        url = f"{self.base_url}/me/accounts"
        
        params = {
            'access_token': user_access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Find the page in the accounts
            for page in data.get('data', []):
                if page.get('id') == self.page_id:
                    return page.get('access_token')
            
            print(f"Page {self.page_id} not found in user's managed pages")
            return None
            
        except requests.RequestException as e:
            print(f"Error getting page access token: {e}")
            return None


class FacebookAPIConfig:
    """Configuration management for Facebook Pages API"""
    
    @staticmethod
    def from_env() -> Optional[FacebookAPI]:
        """Create Facebook API instance from environment variables (legacy)"""
        access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        page_id = os.getenv('FACEBOOK_PAGE_ID')
        
        if not access_token or not page_id:
            print("Missing Facebook API credentials in environment variables")
            print("Required: FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_ID")
            return None
            
        return FacebookAPI(access_token, page_id)
    
    @staticmethod
    def from_account(account) -> Optional[FacebookAPI]:
        """Create Facebook API instance from account credentials"""
        credentials = account.api_credentials
        
        if not credentials.facebook_access_token or not credentials.facebook_page_id:
            return None
            
        return FacebookAPI(credentials.facebook_access_token, credentials.facebook_page_id)