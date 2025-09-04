from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
import time
import random

from models.trend import (
    TrendKeyword, TrendCategory, TrendSource, TrendScore, 
    PlatformMetrics, RegionalData
)
from services.theme_trend_integration import theme_trend_integrator


class RedditTrendsService:
    """Service for fetching food/recipe trends from Reddit"""
    
    def __init__(self, theme_id: str = "food_recipe_general"):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'VoidLoopContentEngine/1.0 (Food trend analysis)'
        })
        self.request_delay = 1.0
        self.theme_id = theme_id
        
        # Food-related subreddits to monitor
        self.food_subreddits = [
            'food', 'recipes', 'MealPrepSunday', 'Cooking', 'FoodPorn',
            'HealthyFood', 'vegetarian', 'vegan', 'ketorecipes', 
            'slowcooking', 'instantpot', 'Baking', 'DessertPorn',
            'GifRecipes', 'EatCheapAndHealthy', 'MealPrepSunday'
        ]
    
    def get_trending_food_topics(self, geo: str = 'US', 
                               timeframe: str = 'day',
                               limit: int = 20) -> List[TrendKeyword]:
        """Get trending food topics from Reddit"""
        trending_keywords = []
        
        for subreddit in self.food_subreddits[:5]:  # Limit to avoid rate limits
            try:
                posts = self._get_hot_posts(subreddit, limit=10)
                for post in posts:
                    title = post.get('title', '')
                    score = post.get('score', 0)
                    
                    if theme_trend_integrator.is_food_related_by_theme(title, self.theme_id) and score > 50:
                        # Extract keywords from title
                        keywords = self._extract_keywords_from_title(title)
                        for keyword in keywords:
                            if len(keyword) > 3 and len(trending_keywords) < limit:
                                trending_keywords.append(
                                    self._create_trend_keyword(
                                        keyword=keyword,
                                        score=min(score / 10, 100),  # Scale Reddit score
                                        geo=geo,
                                        source_url=f"https://reddit.com{post.get('permalink', '')}"
                                    )
                                )
                
                time.sleep(self.request_delay)
                
            except Exception as e:
                print(f"Error fetching from r/{subreddit}: {e}")
                continue
        
        return trending_keywords[:limit]
    
    def search_recipe_trends(self, keywords: List[str], 
                           geo: str = 'US',
                           timeframe: str = 'week') -> List[TrendKeyword]:
        """Search for specific recipe trends on Reddit"""
        trend_results = []
        
        for keyword in keywords[:10]:  # Limit to avoid rate limits
            try:
                # Search across food subreddits
                search_results = self._search_reddit(keyword, 'food,recipes,cooking')
                
                if search_results:
                    total_score = sum(post.get('score', 0) for post in search_results[:5])
                    avg_score = total_score / min(len(search_results), 5) if search_results else 0
                    
                    if avg_score > 10:  # Filter for meaningful engagement
                        trend_results.append(
                            TrendKeyword(
                                keyword=keyword,
                                category=self._categorize_keyword(keyword),
                                score=TrendScore(
                                    current_score=min(avg_score / 5, 100),
                                    peak_score=min(avg_score / 5, 100),
                                    growth_rate=random.uniform(-5, 15)  # Placeholder
                                ),
                                regional_data=[RegionalData(country=geo, score=min(avg_score / 5, 100))],
                                platform_metrics=[PlatformMetrics(
                                    source=TrendSource.REDDIT,
                                    engagement_score=min(avg_score / 5, 100),
                                    last_updated=datetime.now()
                                )],
                                related_keywords=[],
                                first_detected=datetime.now(),
                                last_updated=datetime.now(),
                                is_rising=avg_score > 50
                            )
                        )
                
                time.sleep(self.request_delay + random.uniform(0.5, 1.0))
                
            except Exception as e:
                print(f"Error searching Reddit for '{keyword}': {e}")
                continue
        
        return trend_results
    
    def get_seasonal_recipe_trends(self, geo: str = 'US') -> List[TrendKeyword]:
        """Get seasonal trends from Reddit food communities"""
        current_month = datetime.now().month
        
        # Search for seasonal content
        seasonal_terms = {
            12: ['christmas', 'holiday', 'winter'],
            1: ['new year', 'healthy', 'detox'],
            2: ['valentine', 'chocolate', 'romantic'],
            3: ['spring', 'easter', 'fresh'],
            4: ['spring', 'easter', 'brunch'],
            5: ['mother day', 'spring', 'fresh'],
            6: ['summer', 'grilling', 'fresh fruit'],
            7: ['summer', 'bbq', 'cold'],
            8: ['summer', 'harvest', 'fresh'],
            9: ['fall', 'pumpkin', 'apple'],
            10: ['halloween', 'pumpkin', 'autumn'],
            11: ['thanksgiving', 'turkey', 'fall']
        }
        
        terms = seasonal_terms.get(current_month, ['recipe'])
        return self.search_recipe_trends(terms, geo=geo)
    
    def _get_hot_posts(self, subreddit: str, limit: int = 25) -> List[Dict]:
        """Get hot posts from a subreddit"""
        try:
            url = f'https://www.reddit.com/r/{subreddit}/hot.json'
            params = {'limit': limit}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            if 'data' in data and 'children' in data['data']:
                for post in data['data']['children']:
                    if post.get('kind') == 't3':  # Link post
                        posts.append(post['data'])
            
            return posts
            
        except Exception as e:
            print(f"Error getting hot posts from r/{subreddit}: {e}")
            return []
    
    def _search_reddit(self, query: str, subreddits: str) -> List[Dict]:
        """Search Reddit for specific terms"""
        try:
            url = 'https://www.reddit.com/search.json'
            params = {
                'q': f'{query} subreddit:{subreddits}',
                'sort': 'hot',
                'limit': 10,
                't': 'week'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            if 'data' in data and 'children' in data['data']:
                for post in data['data']['children']:
                    if post.get('kind') == 't3':
                        posts.append(post['data'])
            
            return posts
            
        except Exception as e:
            print(f"Error searching Reddit for '{query}': {e}")
            return []
    
    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """Extract actual recipe/food item keywords from Reddit post title"""
        import re
        
        title_lower = title.lower()
        extracted_keywords = []
        
        # Common recipe title patterns - extract the main dish/ingredient
        patterns = [
            r'recipe for (.+?)(?:\s|$|[.,!?])',
            r'how to make (.+?)(?:\s|$|[.,!?])', 
            r'homemade (.+?)(?:\s|$|[.,!?])',
            r'easy (.+?) recipe',
            r'quick (.+?) recipe',
            r'best (.+?) recipe',
            r'perfect (.+?)(?:\s|$|[.,!?])',
            r'\[.*?\]\s*(.+?)(?:\s|$|[.,!?])',  # [I ate] Pasta Carbonara
        ]
        
        # Try to extract from common patterns first
        for pattern in patterns:
            matches = re.findall(pattern, title_lower)
            for match in matches:
                cleaned = self._clean_recipe_name(match)
                if cleaned and self._is_actual_food_item(cleaned):
                    extracted_keywords.append(cleaned)
        
        # If no patterns matched, try to identify main ingredients/dishes directly
        if not extracted_keywords:
            words = title_lower.replace('[', '').replace(']', '').split()
            
            # Skip generic descriptors and focus on nouns (ingredients/dishes)
            skip_descriptors = {
                'homemade', 'delicious', 'amazing', 'perfect', 'easy', 'quick', 
                'simple', 'best', 'favorite', 'crispy', 'creamy', 'fresh',
                'healthy', 'yummy', 'tasty', 'good', 'great', 'awesome',
                'recipe', 'recipes', 'cooking', 'food', 'meal', 'dish'
            }
            
            for word in words:
                word = word.strip('.,!?()[]{}":;')
                if (len(word) > 3 and 
                    word not in skip_descriptors and 
                    self._is_actual_food_item(word)):
                    extracted_keywords.append(word)
        
        # Deduplicate and limit
        unique_keywords = list(dict.fromkeys(extracted_keywords))  # Preserves order
        return unique_keywords[:2]  # Limit to top 2 most relevant keywords
    
    def _clean_recipe_name(self, name: str) -> str:
        """Clean extracted recipe name"""
        # Remove common prefixes/suffixes
        name = name.strip()
        
        # Remove trailing words that aren't part of the dish name
        stop_words = ['recipe', 'recipes', 'dish', 'meal', 'food', 'cooking']
        words = name.split()
        
        # Remove stop words from the end
        while words and words[-1] in stop_words:
            words.pop()
        
        return ' '.join(words) if words else ''
    
    def _is_actual_food_item(self, text: str) -> bool:
        """Check if text represents an actual ingredient, dish, or recipe name"""
        text_lower = text.strip().lower()
        
        # Skip if too generic or not food-related
        if len(text_lower) < 3:
            return False
        
        # Specific ingredients and dishes (higher priority)
        specific_foods = {
            # Proteins
            'chicken', 'beef', 'pork', 'salmon', 'tuna', 'shrimp', 'tofu', 'eggs',
            'turkey', 'duck', 'lamb', 'bacon', 'ham', 'sausage', 'fish',
            
            # Vegetables
            'broccoli', 'spinach', 'kale', 'carrots', 'onions', 'garlic', 'tomatoes',
            'potatoes', 'mushrooms', 'peppers', 'avocado', 'lettuce', 'cucumber',
            'zucchini', 'eggplant', 'cauliflower', 'asparagus', 'corn',
            
            # Grains/Starches
            'pasta', 'rice', 'quinoa', 'bread', 'noodles', 'couscous', 'barley',
            'oats', 'flour', 'tortilla', 'bagel', 'pizza',
            
            # Fruits
            'apple', 'banana', 'strawberry', 'blueberry', 'orange', 'lemon', 
            'lime', 'berries', 'mango', 'pineapple', 'grapes', 'peach',
            
            # Dairy
            'cheese', 'milk', 'yogurt', 'cream', 'butter', 'mozzarella', 'cheddar',
            'parmesan', 'feta', 'ricotta',
            
            # Specific dishes
            'soup', 'salad', 'sandwich', 'burger', 'tacos', 'enchiladas', 'curry',
            'stir-fry', 'casserole', 'lasagna', 'spaghetti', 'carbonara', 'alfredo',
            'risotto', 'paella', 'chili', 'stew', 'ramen', 'pho', 'sushi',
            'pancakes', 'waffles', 'muffins', 'cookies', 'cake', 'pie', 'brownies',
            
            # Cooking methods with food
            'grilled chicken', 'baked salmon', 'roasted vegetables', 'fried rice',
            'steamed vegetables', 'sautéed mushrooms'
        }
        
        # Check if it's a specific food item
        if any(food in text_lower for food in specific_foods):
            return True
        
        # Check compound food names (adjective + noun pattern)
        food_adjectives = {
            'grilled', 'baked', 'fried', 'roasted', 'steamed', 'sautéed',
            'marinated', 'seasoned', 'stuffed', 'glazed', 'crispy'
        }
        
        words = text_lower.split()
        if len(words) == 2 and words[0] in food_adjectives:
            return self._is_basic_ingredient(words[1])
        
        # Single word ingredient check
        return self._is_basic_ingredient(text_lower)
    
    def _is_basic_ingredient(self, word: str) -> bool:
        """Check if single word is a basic ingredient"""
        basic_ingredients = {
            'chicken', 'beef', 'pork', 'salmon', 'tuna', 'shrimp', 'tofu',
            'broccoli', 'spinach', 'carrots', 'onions', 'garlic', 'tomatoes',
            'pasta', 'rice', 'quinoa', 'cheese', 'eggs', 'avocado', 'mushrooms'
        }
        return word in basic_ingredients
    
    def _is_food_related(self, text: str) -> bool:
        """Check if text contains food/recipe content using theme system"""
        return theme_trend_integrator.is_food_related_by_theme(text, self.theme_id)
    
    def _create_trend_keyword(self, keyword: str, score: float, 
                            geo: str, source_url: str = '') -> TrendKeyword:
        """Create a TrendKeyword object from Reddit data"""
        return TrendKeyword(
            keyword=keyword,
            category=self._categorize_keyword(keyword),
            score=TrendScore(
                current_score=min(float(score), 100.0),
                peak_score=min(float(score), 100.0),
                growth_rate=random.uniform(-5.0, 15.0)
            ),
            platform_metrics=[PlatformMetrics(
                source=TrendSource.REDDIT,
                engagement_score=min(float(score), 100.0),
                last_updated=datetime.now()
            )],
            regional_data=[RegionalData(
                country=geo,
                score=min(float(score), 100.0)
            )],
            related_keywords=[],  # Could extract from comments later
            first_detected=datetime.now(),
            last_updated=datetime.now(),
            is_rising=score > 30
        )
    
    def _categorize_keyword(self, keyword: str) -> TrendCategory:
        """Categorize a keyword using theme system"""
        return theme_trend_integrator.categorize_keyword_from_theme(keyword, self.theme_id)