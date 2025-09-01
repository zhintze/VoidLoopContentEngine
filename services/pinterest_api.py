import requests
import os
from typing import Optional, Dict, Any, List
import json


class PinterestAPI:
    """Pinterest API v5 integration"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.pinterest.com/v5"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get user account information"""
        url = f"{self.base_url}/user_account"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting user info: {e}")
            return {}
    
    def get_boards(self) -> List[Dict[str, Any]]:
        """Get user's boards"""
        url = f"{self.base_url}/boards"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except requests.RequestException as e:
            print(f"Error getting boards: {e}")
            return []
    
    def create_pin(self, board_id: str, title: str, description: str, 
                   image_url: str, link: Optional[str] = None) -> bool:
        """Create a new pin on a board"""
        url = f"{self.base_url}/pins"
        
        pin_data = {
            'board_id': board_id,
            'title': title,
            'description': description,
            'media_source': {
                'source_type': 'image_url',
                'url': image_url
            }
        }
        
        if link:
            pin_data['link'] = link
        
        try:
            response = requests.post(url, headers=self.headers, json=pin_data)
            response.raise_for_status()
            data = response.json()
            print(f"Successfully created pin: {data.get('id')}")
            return True
        except requests.RequestException as e:
            print(f"Error creating pin: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return False
    
    def post_pin(self, board_id: str, title: str, description: str,
                 image_url: str, link: Optional[str] = None) -> bool:
        """Complete workflow: create and post a pin"""
        print(f"Posting to Pinterest: {title[:50]}...")
        return self.create_pin(board_id, title, description, image_url, link)
    
    def find_board_by_name(self, board_name: str) -> Optional[str]:
        """Find a board ID by name"""
        boards = self.get_boards()
        for board in boards:
            if board.get('name', '').lower() == board_name.lower():
                return board.get('id')
        return None


class PinterestAPIConfig:
    """Configuration management for Pinterest API"""
    
    @staticmethod
    def from_env() -> Optional[PinterestAPI]:
        """Create Pinterest API instance from environment variables (legacy)"""
        access_token = os.getenv('PINTEREST_ACCESS_TOKEN')
        
        if not access_token:
            print("Missing Pinterest API credentials in environment variables")
            print("Required: PINTEREST_ACCESS_TOKEN")
            return None
            
        return PinterestAPI(access_token)
    
    @staticmethod
    def from_account(account) -> Optional[PinterestAPI]:
        """Create Pinterest API instance from account credentials"""
        credentials = account.api_credentials
        
        if not credentials.pinterest_access_token:
            return None
            
        return PinterestAPI(credentials.pinterest_access_token)