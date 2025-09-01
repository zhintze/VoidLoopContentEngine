import requests
import os
from typing import Optional, Dict, Any
import json


class TwitterAPI:
    """Twitter/X API v2 integration for posting tweets"""
    
    def __init__(self, bearer_token: str, api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None, access_token: Optional[str] = None,
                 access_token_secret: Optional[str] = None):
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.base_url = "https://api.x.com/2"
        
        # Headers for OAuth 2.0 Bearer Token
        self.headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        url = f"{self.base_url}/users/me"
        
        params = {
            'user.fields': 'id,name,username,public_metrics'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {})
        except requests.RequestException as e:
            print(f"Error getting user info: {e}")
            return {}
    
    def create_tweet(self, text: str, media_ids: Optional[list] = None) -> bool:
        """Create a new tweet"""
        url = f"{self.base_url}/tweets"
        
        payload = {
            'text': text
        }
        
        if media_ids:
            payload['media'] = {
                'media_ids': media_ids
            }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            print(f"Successfully posted to Twitter: {result.get('data', {}).get('id')}")
            return True
        except requests.RequestException as e:
            print(f"Error creating tweet: {e}")
            if hasattr(e, 'response') and e.response:
                try:
                    error_data = e.response.json()
                    print(f"Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Response: {e.response.text}")
            return False
    
    def upload_media(self, image_url: str) -> Optional[str]:
        """Upload media for tweet (requires additional setup)"""
        # Note: Media upload requires OAuth 1.0a and additional authentication
        # This is a placeholder for the media upload functionality
        print("Media upload requires OAuth 1.0a credentials and additional setup")
        print(f"Image URL provided: {image_url}")
        return None
    
    def post_tweet(self, text: str, image_url: Optional[str] = None) -> bool:
        """Complete workflow: create and post tweet"""
        print(f"Posting to Twitter: {text[:50]}...")
        
        # Check character limit
        if len(text) > 280:
            print(f"⚠️ Tweet exceeds 280 characters ({len(text)}). Truncating...")
            text = text[:277] + "..."
        
        media_ids = None
        if image_url:
            # For now, we'll note that media upload needs additional setup
            print("📷 Image posting requires OAuth 1.0a setup (not implemented in this version)")
            
        return self.create_tweet(text, media_ids)
    
    def get_tweet_metrics(self, tweet_id: str) -> Dict[str, Any]:
        """Get metrics for a specific tweet"""
        url = f"{self.base_url}/tweets/{tweet_id}"
        
        params = {
            'tweet.fields': 'public_metrics,created_at'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('data', {})
        except requests.RequestException as e:
            print(f"Error getting tweet metrics: {e}")
            return {}


class TwitterAPIConfig:
    """Configuration management for Twitter/X API"""
    
    @staticmethod
    def from_env() -> Optional[TwitterAPI]:
        """Create Twitter API instance from environment variables (legacy)"""
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        if not bearer_token:
            print("Missing Twitter API credentials in environment variables")
            print("Required: TWITTER_BEARER_TOKEN")
            print("Optional: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET")
            return None
            
        return TwitterAPI(bearer_token, api_key, api_secret, access_token, access_token_secret)
    
    @staticmethod
    def from_account(account) -> Optional[TwitterAPI]:
        """Create Twitter API instance from account credentials"""
        credentials = account.api_credentials
        
        if not credentials.twitter_bearer_token:
            return None
            
        return TwitterAPI(
            credentials.twitter_bearer_token,
            credentials.twitter_api_key,
            credentials.twitter_api_secret,
            credentials.twitter_access_token,
            credentials.twitter_access_token_secret
        )