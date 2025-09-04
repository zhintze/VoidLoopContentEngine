from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
import time
import random
import json
import re

from models.trend import (
    TrendKeyword, TrendCategory, TrendSource, TrendScore, 
    PlatformMetrics, RegionalData
)


class TikTokTrendsService:
    """Service for fetching food/recipe trends from TikTok"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.request_delay = 2.0
        
        # Food-related hashtags to monitor on TikTok
        self.food_hashtags = [
            'foodtok', 'recipe', 'cooking', 'food', 'baking', 'easyrecipe',
            'healthyfood', 'quickrecipe', 'foodhack', 'homecooking', 'foodie',
            'recipeoftiktok', 'viralrecipe', 'food4thought', 'cookingtime',
            'foodlover', 'homemade', 'delicious', 'yummy', 'tasty'
        ]
        
        # Base URLs for TikTok's unofficial API endpoints
        self.base_url = 'https://www.tiktok.com/api'
        
    def get_trending_food_hashtags(self, geo: str = 'US', limit: int = 20) -> List[TrendKeyword]:
        """Get trending food hashtags from TikTok"""
        trending_keywords = []
        
        # Since TikTok's API is restricted, we'll use a combination of 
        # known food hashtags and simulate trend data based on typical patterns
        
        try:
            # Search for each food hashtag and analyze engagement
            for hashtag in self.food_hashtags[:limit]:
                try:
                    # Simulate hashtag data (in real implementation, would use TikTok API)
                    trend_data = self._simulate_hashtag_data(hashtag)
                    
                    if trend_data['view_count'] > 1000000:  # 1M+ views threshold
                        trending_keywords.append(
                            self._create_trend_keyword(
                                keyword=hashtag,
                                score=min(trend_data['view_count'] / 100000, 100),  # Scale views to 0-100
                                geo=geo,
                                view_count=trend_data['view_count'],
                                post_count=trend_data['post_count'],
                                engagement_score=trend_data['engagement_rate'] * 100
                            )
                        )
                    
                    time.sleep(self.request_delay + random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    print(f"Error fetching TikTok data for #{hashtag}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching TikTok trending hashtags: {e}")
        
        return sorted(trending_keywords, key=lambda x: x.score.current_score, reverse=True)[:limit]
    
    def search_recipe_trends(self, keywords: List[str], 
                           geo: str = 'US',
                           timeframe: str = 'week') -> List[TrendKeyword]:
        """Search for specific recipe trends on TikTok"""
        trend_results = []
        
        for keyword in keywords[:10]:  # Limit to avoid rate limits
            try:
                # Convert keyword to hashtag format
                hashtag = self._keyword_to_hashtag(keyword)
                
                # Simulate search results (replace with actual TikTok API call)
                search_data = self._simulate_search_data(keyword, hashtag)
                
                if search_data['relevance_score'] > 0.3:  # Minimum relevance threshold
                    trend_results.append(
                        TrendKeyword(
                            keyword=keyword,
                            category=self._categorize_keyword(keyword),
                            score=TrendScore(
                                current_score=min(search_data['trend_score'], 100),
                                peak_score=min(search_data['trend_score'] * 1.2, 100),
                                growth_rate=search_data['growth_rate']
                            ),
                            regional_data=[RegionalData(
                                country=geo, 
                                score=min(search_data['trend_score'], 100)
                            )],
                            platform_metrics=[PlatformMetrics(
                                source=TrendSource.TIKTOK,
                                engagement_score=search_data['engagement_score'],
                                view_count=search_data['view_count'],
                                post_count=search_data['post_count'],
                                last_updated=datetime.now()
                            )],
                            related_keywords=search_data['related_hashtags'],
                            first_detected=datetime.now(),
                            last_updated=datetime.now(),
                            is_rising=search_data['growth_rate'] > 0
                        )
                    )
                
                time.sleep(self.request_delay + random.uniform(0.5, 1.0))
                
            except Exception as e:
                print(f"Error searching TikTok for '{keyword}': {e}")
                continue
        
        return trend_results
    
    def get_viral_food_content(self, limit: int = 15) -> List[TrendKeyword]:
        """Get viral food content from TikTok"""
        viral_trends = []
        
        # Focus on hashtags that typically go viral
        viral_hashtags = [
            'viralrecipe', 'foodhack', 'recipeoftiktok', 'easyrecipe',
            'quickrecipe', 'foodtok', 'cookingchallenge', 'bakinghack'
        ]
        
        try:
            for hashtag in viral_hashtags[:limit]:
                # Simulate viral content data
                viral_data = self._simulate_viral_content(hashtag)
                
                if viral_data['viral_score'] > 70:  # High viral threshold
                    viral_trends.append(
                        self._create_trend_keyword(
                            keyword=hashtag,
                            score=viral_data['viral_score'],
                            geo='US',
                            view_count=viral_data['view_count'],
                            post_count=viral_data['post_count'],
                            engagement_score=viral_data['engagement_score'],
                            is_rising=True
                        )
                    )
                
                time.sleep(1.0)  # Faster for viral content check
                
        except Exception as e:
            print(f"Error fetching viral TikTok content: {e}")
        
        return sorted(viral_trends, key=lambda x: x.score.current_score, reverse=True)
    
    def _simulate_hashtag_data(self, hashtag: str) -> Dict:
        """Simulate hashtag data (replace with actual API when available)"""
        # Base simulation on realistic TikTok engagement patterns
        base_popularity = {
            'foodtok': 0.9,
            'recipe': 0.8,
            'cooking': 0.7,
            'viralrecipe': 0.85,
            'foodhack': 0.75,
            'easyrecipe': 0.8,
            'healthyfood': 0.6,
            'quickrecipe': 0.7
        }.get(hashtag, 0.5)
        
        # Add randomization to simulate real-world variation
        popularity = base_popularity * random.uniform(0.7, 1.3)
        
        return {
            'view_count': int(popularity * random.uniform(5000000, 50000000)),
            'post_count': int(popularity * random.uniform(10000, 100000)),
            'engagement_rate': min(popularity * random.uniform(0.05, 0.15), 0.15),
            'trending_score': min(popularity * 100, 100)
        }
    
    def _simulate_search_data(self, keyword: str, hashtag: str) -> Dict:
        """Simulate search data for a keyword"""
        # Calculate relevance based on food-related terms
        relevance = self._calculate_food_relevance(keyword)
        
        # Simulate trend metrics
        trend_score = relevance * random.uniform(30, 90)
        view_count = int(trend_score * random.uniform(50000, 500000))
        
        return {
            'relevance_score': relevance,
            'trend_score': trend_score,
            'view_count': view_count,
            'post_count': int(view_count / random.uniform(100, 500)),
            'engagement_score': min(trend_score * random.uniform(0.8, 1.2), 100),
            'growth_rate': random.uniform(-10, 25),
            'related_hashtags': self._generate_related_hashtags(keyword)
        }
    
    def _simulate_viral_content(self, hashtag: str) -> Dict:
        """Simulate viral content metrics"""
        viral_multiplier = random.uniform(1.5, 3.0)  # Viral content has higher engagement
        
        return {
            'viral_score': min(random.uniform(70, 95) * viral_multiplier, 100),
            'view_count': int(random.uniform(1000000, 10000000) * viral_multiplier),
            'post_count': int(random.uniform(5000, 50000)),
            'engagement_score': min(random.uniform(60, 90) * viral_multiplier, 100)
        }
    
    def _keyword_to_hashtag(self, keyword: str) -> str:
        """Convert a keyword to hashtag format"""
        # Remove spaces and special characters, make lowercase
        hashtag = re.sub(r'[^a-zA-Z0-9]', '', keyword.lower())
        return f"#{hashtag}"
    
    def _calculate_food_relevance(self, keyword: str) -> float:
        """Calculate how food-relevant a keyword is"""
        keyword_lower = keyword.lower()
        
        # High relevance food terms
        high_relevance = [
            'recipe', 'cooking', 'baking', 'food', 'meal', 'dish', 'cuisine',
            'ingredient', 'flavor', 'taste', 'breakfast', 'lunch', 'dinner',
            'dessert', 'snack', 'healthy', 'diet', 'nutrition', 'chef',
            'kitchen', 'homemade', 'delicious', 'yummy', 'tasty'
        ]
        
        # Medium relevance terms
        medium_relevance = [
            'easy', 'quick', 'simple', 'homemade', 'fresh', 'organic',
            'natural', 'traditional', 'comfort', 'spicy', 'sweet', 'savory'
        ]
        
        # Calculate relevance score
        relevance = 0.0
        
        for term in high_relevance:
            if term in keyword_lower:
                relevance += 0.3
        
        for term in medium_relevance:
            if term in keyword_lower:
                relevance += 0.15
        
        # Check for specific ingredients or dishes
        if self._contains_specific_food_item(keyword_lower):
            relevance += 0.4
        
        return min(relevance, 1.0)
    
    def _contains_specific_food_item(self, keyword: str) -> bool:
        """Check if keyword contains specific food items"""
        food_items = [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'shrimp', 'pasta',
            'rice', 'pizza', 'burger', 'sandwich', 'salad', 'soup', 'cake',
            'cookie', 'bread', 'cheese', 'chocolate', 'fruit', 'vegetable',
            'potato', 'tomato', 'onion', 'garlic', 'egg', 'milk', 'butter'
        ]
        
        return any(food in keyword for food in food_items)
    
    def _generate_related_hashtags(self, keyword: str) -> List[str]:
        """Generate related hashtags for a keyword"""
        base_hashtags = ['foodtok', 'recipe', 'cooking', 'food', 'yummy']
        
        # Add keyword-specific hashtags
        keyword_lower = keyword.lower()
        
        if 'healthy' in keyword_lower:
            base_hashtags.extend(['healthyfood', 'wellness', 'nutrition'])
        if 'quick' in keyword_lower or 'easy' in keyword_lower:
            base_hashtags.extend(['quickrecipe', 'easyrecipe', 'fastfood'])
        if 'dessert' in keyword_lower or 'sweet' in keyword_lower:
            base_hashtags.extend(['dessert', 'sweet', 'baking'])
        
        return base_hashtags[:5]  # Return top 5 related hashtags
    
    def _create_trend_keyword(self, keyword: str, score: float, geo: str,
                            view_count: int = None, post_count: int = None,
                            engagement_score: float = None, is_rising: bool = None) -> TrendKeyword:
        """Create a TrendKeyword object from TikTok data"""
        return TrendKeyword(
            keyword=keyword,
            category=self._categorize_keyword(keyword),
            score=TrendScore(
                current_score=min(float(score), 100.0),
                peak_score=min(float(score) * 1.1, 100.0),
                growth_rate=random.uniform(-5.0, 20.0) if is_rising is None else (
                    random.uniform(5.0, 20.0) if is_rising else random.uniform(-10.0, 5.0)
                )
            ),
            platform_metrics=[PlatformMetrics(
                source=TrendSource.TIKTOK,
                engagement_score=engagement_score or min(float(score), 100.0),
                view_count=view_count,
                post_count=post_count,
                last_updated=datetime.now()
            )],
            regional_data=[RegionalData(
                country=geo,
                score=min(float(score), 100.0)
            )],
            related_keywords=self._generate_related_hashtags(keyword),
            first_detected=datetime.now(),
            last_updated=datetime.now(),
            is_rising=is_rising if is_rising is not None else score > 60
        )
    
    def _categorize_keyword(self, keyword: str) -> TrendCategory:
        """Categorize a keyword into appropriate TrendCategory"""
        keyword_lower = keyword.lower()
        
        category_mapping = {
            TrendCategory.VIRAL_RECIPES: ['viral', 'tiktok', 'trending', 'famous', 'popular', 'foodtok'],
            TrendCategory.QUICK_MEALS: ['quick', 'easy', 'fast', 'minute', 'instant', 'hack'],
            TrendCategory.HEALTHY_EATING: ['healthy', 'diet', 'nutrition', 'wellness', 'fit', 'clean'],
            TrendCategory.DESSERTS: ['dessert', 'sweet', 'cake', 'cookie', 'chocolate', 'baking'],
            TrendCategory.COOKING_TECHNIQUES: ['cooking', 'baking', 'grilling', 'frying', 'technique'],
            TrendCategory.COMFORT_FOOD: ['comfort', 'cozy', 'hearty', 'traditional'],
            TrendCategory.INTERNATIONAL: ['asian', 'italian', 'mexican', 'indian', 'thai', 'korean'],
            TrendCategory.INGREDIENTS: ['chicken', 'beef', 'pasta', 'rice', 'vegetable', 'fruit']
        }
        
        for category, terms in category_mapping.items():
            if any(term in keyword_lower for term in terms):
                return category
        
        return TrendCategory.VIRAL_RECIPES  # Default for TikTok content