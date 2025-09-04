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


class PinterestTrendsService:
    """Service for fetching food/recipe trends from Pinterest"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        self.request_delay = 1.5
        
        # Food categories that perform well on Pinterest
        self.pinterest_food_categories = [
            'recipe', 'dinner recipe', 'dessert recipe', 'healthy recipe',
            'easy recipe', 'quick recipe', 'meal prep', 'baking recipe',
            'breakfast recipe', 'lunch recipe', 'appetizer recipe',
            'cocktail recipe', 'smoothie recipe', 'salad recipe',
            'soup recipe', 'pasta recipe', 'chicken recipe', 'vegetarian recipe'
        ]
        
        # Seasonal food trends popular on Pinterest
        self.seasonal_trends = {
            'spring': ['easter recipes', 'spring vegetables', 'fresh herbs', 'asparagus recipes'],
            'summer': ['grilling recipes', 'summer salads', 'fresh fruit', 'iced drinks', 'bbq recipes'],
            'fall': ['pumpkin recipes', 'apple recipes', 'comfort food', 'soup recipes'],
            'winter': ['holiday baking', 'warm drinks', 'comfort food', 'holiday cookies']
        }
        
    def get_trending_food_pins(self, geo: str = 'US', limit: int = 20) -> List[TrendKeyword]:
        """Get trending food pins from Pinterest"""
        trending_keywords = []
        
        try:
            # Pinterest is very visual - focus on recipe categories that perform well
            for category in self.pinterest_food_categories[:limit]:
                try:
                    # Simulate Pinterest trend data (replace with actual API when available)
                    pin_data = self._simulate_pin_trend_data(category)
                    
                    if pin_data['save_count'] > 10000:  # Minimum saves threshold
                        trending_keywords.append(
                            self._create_trend_keyword(
                                keyword=category,
                                score=min(pin_data['save_count'] / 1000, 100),  # Scale saves to 0-100
                                geo=geo,
                                save_count=pin_data['save_count'],
                                pin_count=pin_data['pin_count'],
                                engagement_score=pin_data['engagement_rate'] * 100
                            )
                        )
                    
                    time.sleep(self.request_delay + random.uniform(0.3, 0.8))
                    
                except Exception as e:
                    print(f"Error fetching Pinterest data for '{category}': {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching Pinterest trending pins: {e}")
        
        return sorted(trending_keywords, key=lambda x: x.score.current_score, reverse=True)[:limit]
    
    def search_recipe_trends(self, keywords: List[str], 
                           geo: str = 'US',
                           timeframe: str = 'week') -> List[TrendKeyword]:
        """Search for specific recipe trends on Pinterest"""
        trend_results = []
        
        for keyword in keywords[:10]:  # Limit to avoid rate limits
            try:
                # Enhance keyword for Pinterest (add "recipe" if not present)
                pinterest_keyword = self._enhance_keyword_for_pinterest(keyword)
                
                # Simulate Pinterest search data
                search_data = self._simulate_pinterest_search(pinterest_keyword, keyword)
                
                if search_data['relevance_score'] > 0.4:  # Pinterest relevance threshold
                    trend_results.append(
                        TrendKeyword(
                            keyword=keyword,
                            category=self._categorize_keyword(keyword),
                            score=TrendScore(
                                current_score=min(search_data['trend_score'], 100),
                                peak_score=min(search_data['trend_score'] * 1.15, 100),
                                growth_rate=search_data['growth_rate']
                            ),
                            regional_data=[RegionalData(
                                country=geo, 
                                score=min(search_data['trend_score'], 100)
                            )],
                            platform_metrics=[PlatformMetrics(
                                source=TrendSource.PINTEREST,
                                engagement_score=search_data['engagement_score'],
                                view_count=search_data['impression_count'],
                                post_count=search_data['pin_count'],
                                share_count=search_data['save_count'],
                                last_updated=datetime.now()
                            )],
                            related_keywords=search_data['related_terms'],
                            first_detected=datetime.now(),
                            last_updated=datetime.now(),
                            is_rising=search_data['growth_rate'] > 0
                        )
                    )
                
                time.sleep(self.request_delay + random.uniform(0.5, 1.0))
                
            except Exception as e:
                print(f"Error searching Pinterest for '{keyword}': {e}")
                continue
        
        return trend_results
    
    def get_seasonal_recipe_trends(self, geo: str = 'US') -> List[TrendKeyword]:
        """Get seasonal recipe trends from Pinterest"""
        current_month = datetime.now().month
        
        # Determine current season
        if current_month in [3, 4, 5]:
            season = 'spring'
        elif current_month in [6, 7, 8]:
            season = 'summer'
        elif current_month in [9, 10, 11]:
            season = 'fall'
        else:
            season = 'winter'
        
        seasonal_keywords = self.seasonal_trends.get(season, [])
        
        # Add next season's trends (Pinterest users plan ahead)
        next_season_map = {
            'spring': 'summer',
            'summer': 'fall', 
            'fall': 'winter',
            'winter': 'spring'
        }
        next_season = next_season_map[season]
        seasonal_keywords.extend(self.seasonal_trends.get(next_season, [])[:2])
        
        return self.search_recipe_trends(seasonal_keywords, geo=geo)
    
    def get_pinterest_food_trends_by_category(self, category: TrendCategory, 
                                            limit: int = 15) -> List[TrendKeyword]:
        """Get Pinterest trends for a specific food category"""
        category_keywords = self._get_pinterest_category_keywords(category)
        
        trends = []
        for keyword in category_keywords[:limit]:
            try:
                trend_data = self._simulate_pinterest_category_trend(keyword, category)
                
                if trend_data['pinterest_score'] > 50:  # Pinterest-specific threshold
                    trends.append(
                        self._create_trend_keyword(
                            keyword=keyword,
                            score=trend_data['pinterest_score'],
                            geo='US',
                            save_count=trend_data['save_count'],
                            pin_count=trend_data['pin_count'],
                            engagement_score=trend_data['engagement_score']
                        )
                    )
                
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Error fetching Pinterest category trend for '{keyword}': {e}")
                continue
        
        return sorted(trends, key=lambda x: x.score.current_score, reverse=True)
    
    def _simulate_pin_trend_data(self, category: str) -> Dict:
        """Simulate Pinterest pin trend data"""
        # Base popularity on Pinterest food category performance
        base_popularity = {
            'recipe': 0.9,
            'dinner recipe': 0.85,
            'dessert recipe': 0.9,
            'healthy recipe': 0.8,
            'easy recipe': 0.85,
            'meal prep': 0.75,
            'baking recipe': 0.8,
            'breakfast recipe': 0.7,
            'quick recipe': 0.75
        }.get(category, 0.6)
        
        # Pinterest has high engagement for visual content
        popularity = base_popularity * random.uniform(0.8, 1.2)
        
        return {
            'save_count': int(popularity * random.uniform(20000, 200000)),
            'pin_count': int(popularity * random.uniform(50000, 500000)),
            'impression_count': int(popularity * random.uniform(500000, 5000000)),
            'engagement_rate': min(popularity * random.uniform(0.03, 0.08), 0.08),  # Pinterest has lower but high-quality engagement
            'trending_score': min(popularity * 100, 100)
        }
    
    def _simulate_pinterest_search(self, pinterest_keyword: str, original_keyword: str) -> Dict:
        """Simulate Pinterest search data"""
        # Calculate Pinterest-specific relevance
        relevance = self._calculate_pinterest_relevance(original_keyword)
        
        # Pinterest users search for specific, actionable content
        visual_appeal = self._calculate_visual_appeal(original_keyword)
        
        combined_score = (relevance * 0.7) + (visual_appeal * 0.3)
        trend_score = combined_score * random.uniform(40, 95)
        
        return {
            'relevance_score': relevance,
            'trend_score': trend_score,
            'save_count': int(trend_score * random.uniform(100, 2000)),
            'pin_count': int(trend_score * random.uniform(200, 5000)),
            'impression_count': int(trend_score * random.uniform(1000, 50000)),
            'engagement_score': min(trend_score * random.uniform(0.9, 1.1), 100),
            'growth_rate': random.uniform(-8, 20),
            'related_terms': self._generate_pinterest_related_terms(original_keyword)
        }
    
    def _simulate_pinterest_category_trend(self, keyword: str, category: TrendCategory) -> Dict:
        """Simulate Pinterest category-specific trend data"""
        # Pinterest performance varies by category
        category_multipliers = {
            TrendCategory.DESSERTS: 1.3,  # Desserts are very popular on Pinterest
            TrendCategory.HEALTHY_EATING: 1.1,
            TrendCategory.QUICK_MEALS: 1.0,
            TrendCategory.COMFORT_FOOD: 0.9,
            TrendCategory.INTERNATIONAL: 0.8,
            TrendCategory.SEASONAL: 1.2,
            TrendCategory.VIRAL_RECIPES: 1.4
        }
        
        multiplier = category_multipliers.get(category, 1.0)
        base_score = random.uniform(50, 85) * multiplier
        
        return {
            'pinterest_score': min(base_score, 100),
            'save_count': int(base_score * random.uniform(500, 5000)),
            'pin_count': int(base_score * random.uniform(1000, 10000)),
            'engagement_score': min(base_score * random.uniform(1.0, 1.3), 100)
        }
    
    def _enhance_keyword_for_pinterest(self, keyword: str) -> str:
        """Enhance keyword for Pinterest search (Pinterest users search specifically)"""
        keyword_lower = keyword.lower()
        
        # Add "recipe" if it's clearly a food item but doesn't have recipe
        if not any(word in keyword_lower for word in ['recipe', 'how to', 'diy']):
            if self._is_food_item(keyword_lower):
                return f"{keyword} recipe"
        
        return keyword
    
    def _calculate_pinterest_relevance(self, keyword: str) -> float:
        """Calculate Pinterest-specific relevance score"""
        keyword_lower = keyword.lower()
        
        # Pinterest-specific high-performing terms
        pinterest_terms = [
            'recipe', 'easy', 'quick', 'healthy', 'homemade', 'diy',
            'step by step', 'how to make', 'best', 'perfect', 'ultimate',
            'simple', 'delicious', 'yummy', 'tasty', 'amazing'
        ]
        
        # Visual appeal terms (Pinterest is visual)
        visual_terms = [
            'beautiful', 'gorgeous', 'stunning', 'pretty', 'colorful',
            'rustic', 'elegant', 'festive', 'cozy', 'aesthetic'
        ]
        
        relevance = 0.0
        
        for term in pinterest_terms:
            if term in keyword_lower:
                relevance += 0.2
        
        for term in visual_terms:
            if term in keyword_lower:
                relevance += 0.15
        
        # Pinterest users love specific, actionable content
        if 'recipe' in keyword_lower:
            relevance += 0.3
        
        return min(relevance, 1.0)
    
    def _calculate_visual_appeal(self, keyword: str) -> float:
        """Calculate visual appeal score for Pinterest"""
        keyword_lower = keyword.lower()
        
        # Foods that are visually appealing on Pinterest
        high_visual_foods = [
            'cake', 'cupcake', 'pie', 'tart', 'cookie', 'brownie',
            'smoothie', 'bowl', 'salad', 'charcuterie', 'pizza',
            'pasta', 'sushi', 'bread', 'muffin', 'pancake'
        ]
        
        visual_descriptors = [
            'colorful', 'layered', 'decorated', 'garnished', 'plated',
            'styled', 'instagram', 'photogenic', 'beautiful'
        ]
        
        visual_score = 0.3  # Base visual appeal
        
        for food in high_visual_foods:
            if food in keyword_lower:
                visual_score += 0.4
                break
        
        for descriptor in visual_descriptors:
            if descriptor in keyword_lower:
                visual_score += 0.3
                break
        
        return min(visual_score, 1.0)
    
    def _is_food_item(self, keyword: str) -> bool:
        """Check if keyword represents a food item"""
        food_items = [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'rice',
            'pizza', 'cake', 'cookie', 'bread', 'soup', 'salad', 'sandwich',
            'burger', 'taco', 'pie', 'muffin', 'pancake', 'waffle',
            'smoothie', 'juice', 'coffee', 'tea', 'chocolate', 'cheese'
        ]
        
        return any(food in keyword for food in food_items)
    
    def _get_pinterest_category_keywords(self, category: TrendCategory) -> List[str]:
        """Get Pinterest-optimized keywords for a category"""
        category_keywords = {
            TrendCategory.DESSERTS: [
                'chocolate cake recipe', 'easy cookies', 'homemade pie',
                'cupcake decorating', 'brownie recipe', 'cheesecake recipe'
            ],
            TrendCategory.HEALTHY_EATING: [
                'healthy meal prep', 'green smoothie', 'quinoa bowl',
                'kale salad', 'overnight oats', 'chia pudding'
            ],
            TrendCategory.QUICK_MEALS: [
                '30 minute meals', 'easy dinner', 'quick breakfast',
                'simple lunch', 'fast recipe', 'one pot meal'
            ],
            TrendCategory.COMFORT_FOOD: [
                'mac and cheese', 'chicken pot pie', 'meatloaf recipe',
                'beef stew', 'homemade pizza', 'grilled cheese'
            ],
            TrendCategory.SEASONAL: [
                'holiday cookies', 'pumpkin spice', 'summer salads',
                'grilling recipes', 'thanksgiving sides', 'easter recipes'
            ]
        }
        
        return category_keywords.get(category, self.pinterest_food_categories[:6])
    
    def _generate_pinterest_related_terms(self, keyword: str) -> List[str]:
        """Generate Pinterest-style related search terms"""
        base_terms = ['easy', 'homemade', 'best', 'simple', 'quick']
        
        keyword_lower = keyword.lower()
        
        # Add context-specific terms
        if 'healthy' in keyword_lower:
            base_terms.extend(['clean eating', 'nutritious', 'wholesome'])
        if 'dessert' in keyword_lower or 'sweet' in keyword_lower:
            base_terms.extend(['decadent', 'indulgent', 'treat'])
        if 'recipe' not in keyword_lower:
            base_terms.append(f"{keyword} recipe")
        
        return base_terms[:5]
    
    def _create_trend_keyword(self, keyword: str, score: float, geo: str,
                            save_count: int = None, pin_count: int = None,
                            engagement_score: float = None) -> TrendKeyword:
        """Create a TrendKeyword object from Pinterest data"""
        return TrendKeyword(
            keyword=keyword,
            category=self._categorize_keyword(keyword),
            score=TrendScore(
                current_score=min(float(score), 100.0),
                peak_score=min(float(score) * 1.1, 100.0),
                growth_rate=random.uniform(-5.0, 15.0)
            ),
            platform_metrics=[PlatformMetrics(
                source=TrendSource.PINTEREST,
                engagement_score=engagement_score or min(float(score), 100.0),
                share_count=save_count,  # Pinterest "saves" are like shares
                post_count=pin_count,
                last_updated=datetime.now()
            )],
            regional_data=[RegionalData(
                country=geo,
                score=min(float(score), 100.0)
            )],
            related_keywords=self._generate_pinterest_related_terms(keyword),
            first_detected=datetime.now(),
            last_updated=datetime.now(),
            is_rising=score > 65  # Pinterest trends tend to be more stable
        )
    
    def _categorize_keyword(self, keyword: str) -> TrendCategory:
        """Categorize a keyword into appropriate TrendCategory"""
        keyword_lower = keyword.lower()
        
        category_mapping = {
            TrendCategory.DESSERTS: ['dessert', 'cake', 'cookie', 'pie', 'sweet', 'chocolate', 'baking'],
            TrendCategory.HEALTHY_EATING: ['healthy', 'clean', 'nutritious', 'diet', 'wellness', 'superfood'],
            TrendCategory.QUICK_MEALS: ['quick', 'easy', 'fast', 'simple', 'minute', 'instant'],
            TrendCategory.COMFORT_FOOD: ['comfort', 'cozy', 'hearty', 'traditional', 'homestyle'],
            TrendCategory.SEASONAL: ['holiday', 'christmas', 'thanksgiving', 'easter', 'seasonal'],
            TrendCategory.INTERNATIONAL: ['italian', 'asian', 'mexican', 'mediterranean', 'french'],
            TrendCategory.COOKING_TECHNIQUES: ['baking', 'grilling', 'roasting', 'slow cooker', 'instant pot']
        }
        
        for category, terms in category_mapping.items():
            if any(term in keyword_lower for term in terms):
                return category
        
        return TrendCategory.VIRAL_RECIPES  # Default category