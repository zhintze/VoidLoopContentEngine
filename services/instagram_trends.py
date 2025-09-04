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


class InstagramTrendsService:
    """Service for fetching food/recipe trends from Instagram"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        self.request_delay = 2.5  # Instagram has stricter rate limits
        
        # Popular food hashtags on Instagram
        self.food_hashtags = [
            'food', 'foodie', 'instafood', 'foodstagram', 'yummy', 'delicious',
            'foodporn', 'homemade', 'cooking', 'recipe', 'healthyfood', 'foodblogger',
            'foodphotography', 'tasty', 'dinner', 'lunch', 'breakfast', 'dessert',
            'foodlover', 'chef', 'restaurant', 'foodgasm', 'eats', 'nomnom',
            'organic', 'vegan', 'vegetarian', 'keto', 'paleo', 'glutenfree'
        ]
        
        # Food influencer categories (typical Instagram food accounts)
        self.influencer_categories = [
            'food_blogger', 'chef', 'home_cook', 'nutritionist', 'baker',
            'food_photographer', 'restaurant', 'food_brand', 'meal_prep'
        ]
        
        # Instagram-specific food trends (often visual-first)
        self.visual_food_trends = [
            'smoothie bowls', 'charcuterie boards', 'rainbow foods', 'flat lay food',
            'overhead food shots', 'food styling', 'aesthetic meals', 'colorful food',
            'minimalist plating', 'rustic food photography'
        ]
        
    def get_trending_food_hashtags(self, geo: str = 'US', limit: int = 20) -> List[TrendKeyword]:
        """Get trending food hashtags from Instagram"""
        trending_keywords = []
        
        try:
            # Focus on food hashtags that are currently performing well
            for hashtag in self.food_hashtags[:limit]:
                try:
                    # Simulate Instagram hashtag performance data
                    hashtag_data = self._simulate_hashtag_performance(hashtag)
                    
                    if hashtag_data['post_count'] > 100000:  # Minimum post count threshold
                        trending_keywords.append(
                            self._create_trend_keyword(
                                keyword=hashtag,
                                score=min(hashtag_data['engagement_rate'] * 1000, 100),  # Scale engagement to 0-100
                                geo=geo,
                                post_count=hashtag_data['post_count'],
                                view_count=hashtag_data['reach'],
                                engagement_score=hashtag_data['engagement_rate'] * 100,
                                share_count=hashtag_data['shares']
                            )
                        )
                    
                    time.sleep(self.request_delay + random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    print(f"Error fetching Instagram data for #{hashtag}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching Instagram trending hashtags: {e}")
        
        return sorted(trending_keywords, key=lambda x: x.score.current_score, reverse=True)[:limit]
    
    def search_recipe_trends(self, keywords: List[str], 
                           geo: str = 'US',
                           timeframe: str = 'week') -> List[TrendKeyword]:
        """Search for specific recipe trends on Instagram"""
        trend_results = []
        
        for keyword in keywords[:10]:  # Limit to avoid rate limits
            try:
                # Convert keyword to Instagram-friendly hashtag
                instagram_hashtag = self._keyword_to_instagram_hashtag(keyword)
                
                # Simulate Instagram search data
                search_data = self._simulate_instagram_search(keyword, instagram_hashtag)
                
                if search_data['relevance_score'] > 0.35:  # Instagram relevance threshold
                    trend_results.append(
                        TrendKeyword(
                            keyword=keyword,
                            category=self._categorize_keyword(keyword),
                            score=TrendScore(
                                current_score=min(search_data['trend_score'], 100),
                                peak_score=min(search_data['trend_score'] * 1.25, 100),
                                growth_rate=search_data['growth_rate']
                            ),
                            regional_data=[RegionalData(
                                country=geo, 
                                score=min(search_data['trend_score'], 100)
                            )],
                            platform_metrics=[PlatformMetrics(
                                source=TrendSource.INSTAGRAM,
                                engagement_score=search_data['engagement_score'],
                                view_count=search_data['reach'],
                                post_count=search_data['post_count'],
                                share_count=search_data['shares'],
                                comment_count=search_data['comments'],
                                last_updated=datetime.now()
                            )],
                            related_keywords=search_data['related_hashtags'],
                            first_detected=datetime.now(),
                            last_updated=datetime.now(),
                            is_rising=search_data['growth_rate'] > 0
                        )
                    )
                
                time.sleep(self.request_delay + random.uniform(0.8, 1.5))
                
            except Exception as e:
                print(f"Error searching Instagram for '{keyword}': {e}")
                continue
        
        return trend_results
    
    def get_food_influencer_trends(self, category: str = 'food_blogger', limit: int = 10) -> List[TrendKeyword]:
        """Get trending content from food influencers"""
        influencer_trends = []
        
        # Simulate trending content from different influencer categories
        category_keywords = self._get_influencer_category_keywords(category)
        
        try:
            for keyword in category_keywords[:limit]:
                # Simulate influencer trend data
                trend_data = self._simulate_influencer_trend(keyword, category)
                
                if trend_data['influence_score'] > 60:  # High influence threshold
                    influencer_trends.append(
                        self._create_trend_keyword(
                            keyword=keyword,
                            score=trend_data['influence_score'],
                            geo='US',
                            post_count=trend_data['posts'],
                            view_count=trend_data['reach'],
                            engagement_score=trend_data['engagement'],
                            share_count=trend_data['shares']
                        )
                    )
                
                time.sleep(1.5)
                
        except Exception as e:
            print(f"Error fetching Instagram influencer trends: {e}")
        
        return sorted(influencer_trends, key=lambda x: x.score.current_score, reverse=True)
    
    def get_visual_food_trends(self, limit: int = 15) -> List[TrendKeyword]:
        """Get visual food trends that perform well on Instagram"""
        visual_trends = []
        
        try:
            for trend in self.visual_food_trends[:limit]:
                # Instagram is highly visual - these trends perform well
                visual_data = self._simulate_visual_trend_performance(trend)
                
                if visual_data['visual_appeal_score'] > 70:
                    visual_trends.append(
                        self._create_trend_keyword(
                            keyword=trend,
                            score=visual_data['visual_appeal_score'],
                            geo='US',
                            post_count=visual_data['post_count'],
                            view_count=visual_data['views'],
                            engagement_score=visual_data['engagement']
                        )
                    )
                
                time.sleep(1.0)
                
        except Exception as e:
            print(f"Error fetching Instagram visual trends: {e}")
        
        return sorted(visual_trends, key=lambda x: x.score.current_score, reverse=True)
    
    def _simulate_hashtag_performance(self, hashtag: str) -> Dict:
        """Simulate Instagram hashtag performance data"""
        # Base popularity on typical Instagram food hashtag performance
        base_performance = {
            'food': 0.95,
            'foodie': 0.9,
            'instafood': 0.85,
            'recipe': 0.8,
            'healthyfood': 0.75,
            'homemade': 0.7,
            'cooking': 0.75,
            'yummy': 0.8,
            'delicious': 0.8,
            'foodporn': 0.85
        }.get(hashtag, 0.6)
        
        # Add variation for realistic simulation
        performance = base_performance * random.uniform(0.7, 1.3)
        
        return {
            'post_count': int(performance * random.uniform(500000, 5000000)),
            'reach': int(performance * random.uniform(1000000, 20000000)),
            'engagement_rate': min(performance * random.uniform(0.02, 0.08), 0.1),  # Instagram engagement rates
            'shares': int(performance * random.uniform(10000, 200000)),
            'comments': int(performance * random.uniform(50000, 500000))
        }
    
    def _simulate_instagram_search(self, keyword: str, hashtag: str) -> Dict:
        """Simulate Instagram search data for a keyword"""
        # Calculate Instagram-specific relevance
        relevance = self._calculate_instagram_relevance(keyword)
        
        # Visual appeal is crucial on Instagram
        visual_score = self._calculate_visual_appeal_score(keyword)
        
        # Combine relevance and visual appeal
        combined_score = (relevance * 0.6) + (visual_score * 0.4)
        trend_score = combined_score * random.uniform(35, 90)
        
        return {
            'relevance_score': relevance,
            'trend_score': trend_score,
            'post_count': int(trend_score * random.uniform(1000, 50000)),
            'reach': int(trend_score * random.uniform(10000, 1000000)),
            'engagement_score': min(trend_score * random.uniform(0.9, 1.2), 100),
            'shares': int(trend_score * random.uniform(100, 5000)),
            'comments': int(trend_score * random.uniform(500, 20000)),
            'growth_rate': random.uniform(-12, 25),
            'related_hashtags': self._generate_instagram_related_hashtags(keyword)
        }
    
    def _simulate_influencer_trend(self, keyword: str, category: str) -> Dict:
        """Simulate influencer trend data"""
        # Different influencer categories have different reach
        category_multipliers = {
            'food_blogger': 1.2,
            'chef': 1.4,
            'home_cook': 1.0,
            'nutritionist': 1.1,
            'baker': 1.3,
            'restaurant': 1.5
        }
        
        multiplier = category_multipliers.get(category, 1.0)
        base_score = random.uniform(50, 80) * multiplier
        
        return {
            'influence_score': min(base_score, 100),
            'posts': int(base_score * random.uniform(10, 200)),
            'reach': int(base_score * random.uniform(50000, 1000000)),
            'engagement': min(base_score * random.uniform(1.0, 1.5), 100),
            'shares': int(base_score * random.uniform(100, 10000))
        }
    
    def _simulate_visual_trend_performance(self, trend: str) -> Dict:
        """Simulate visual trend performance on Instagram"""
        # Visual trends perform very well on Instagram
        visual_multiplier = random.uniform(1.3, 2.0)
        base_score = random.uniform(60, 85) * visual_multiplier
        
        return {
            'visual_appeal_score': min(base_score, 100),
            'post_count': int(base_score * random.uniform(5000, 100000)),
            'views': int(base_score * random.uniform(100000, 2000000)),
            'engagement': min(base_score * random.uniform(1.2, 1.8), 100)
        }
    
    def _keyword_to_instagram_hashtag(self, keyword: str) -> str:
        """Convert keyword to Instagram hashtag format"""
        # Remove spaces, make lowercase, add #
        hashtag = re.sub(r'[^a-zA-Z0-9]', '', keyword.lower())
        return f"#{hashtag}"
    
    def _calculate_instagram_relevance(self, keyword: str) -> float:
        """Calculate Instagram-specific relevance score"""
        keyword_lower = keyword.lower()
        
        # Instagram food-related terms
        instagram_food_terms = [
            'food', 'recipe', 'cooking', 'homemade', 'healthy', 'delicious',
            'yummy', 'tasty', 'fresh', 'organic', 'breakfast', 'lunch', 'dinner',
            'dessert', 'snack', 'meal', 'nutrition', 'diet', 'lifestyle'
        ]
        
        # Instagram engagement terms
        engagement_terms = [
            'easy', 'quick', 'simple', 'amazing', 'perfect', 'best', 'love',
            'favorite', 'must try', 'obsessed', 'craving', 'satisfying'
        ]
        
        relevance = 0.0
        
        for term in instagram_food_terms:
            if term in keyword_lower:
                relevance += 0.25
        
        for term in engagement_terms:
            if term in keyword_lower:
                relevance += 0.15
        
        return min(relevance, 1.0)
    
    def _calculate_visual_appeal_score(self, keyword: str) -> float:
        """Calculate visual appeal score for Instagram"""
        keyword_lower = keyword.lower()
        
        # Highly visual foods that perform well on Instagram
        visual_foods = [
            'smoothie bowl', 'acai bowl', 'charcuterie', 'rainbow', 'colorful',
            'aesthetic', 'pretty', 'beautiful', 'gorgeous', 'stunning',
            'cake', 'cupcake', 'macarons', 'latte art', 'plating', 'styled'
        ]
        
        # Visual composition terms
        composition_terms = [
            'flat lay', 'overhead', 'styled', 'arranged', 'decorated',
            'garnished', 'minimalist', 'rustic', 'elegant', 'artistic'
        ]
        
        visual_score = 0.4  # Base visual appeal
        
        for food in visual_foods:
            if food in keyword_lower:
                visual_score += 0.3
                break
        
        for term in composition_terms:
            if term in keyword_lower:
                visual_score += 0.3
                break
        
        return min(visual_score, 1.0)
    
    def _get_influencer_category_keywords(self, category: str) -> List[str]:
        """Get keywords for different influencer categories"""
        category_keywords = {
            'food_blogger': [
                'food review', 'restaurant visit', 'recipe creation', 'food styling',
                'cooking tips', 'ingredient spotlight'
            ],
            'chef': [
                'chef special', 'professional cooking', 'culinary technique',
                'signature dish', 'kitchen secrets', 'chef tips'
            ],
            'home_cook': [
                'home cooking', 'family recipe', 'weeknight dinner',
                'budget meals', 'cooking from scratch', 'comfort food'
            ],
            'nutritionist': [
                'healthy eating', 'nutrition facts', 'balanced meals',
                'superfood', 'meal planning', 'wellness tips'
            ],
            'baker': [
                'fresh baked', 'artisan bread', 'pastry making',
                'cake decorating', 'sourdough', 'baking tips'
            ]
        }
        
        return category_keywords.get(category, self.food_hashtags[:6])
    
    def _generate_instagram_related_hashtags(self, keyword: str) -> List[str]:
        """Generate Instagram-style related hashtags"""
        base_hashtags = ['food', 'foodie', 'instafood', 'yummy', 'delicious']
        
        keyword_lower = keyword.lower()
        
        # Add context-specific hashtags
        if 'healthy' in keyword_lower:
            base_hashtags.extend(['healthyfood', 'wellness', 'nutrition', 'cleaneating'])
        if 'easy' in keyword_lower or 'quick' in keyword_lower:
            base_hashtags.extend(['easyrecipe', 'quickmeal', 'simple'])
        if 'dessert' in keyword_lower or 'sweet' in keyword_lower:
            base_hashtags.extend(['dessert', 'sweet', 'treat', 'indulgent'])
        if 'homemade' in keyword_lower:
            base_hashtags.extend(['homemade', 'fromscratch', 'homecooking'])
        
        return base_hashtags[:8]  # Instagram allows up to 30 hashtags, but 8-12 is optimal
    
    def _create_trend_keyword(self, keyword: str, score: float, geo: str,
                            post_count: int = None, view_count: int = None,
                            engagement_score: float = None, share_count: int = None) -> TrendKeyword:
        """Create a TrendKeyword object from Instagram data"""
        return TrendKeyword(
            keyword=keyword,
            category=self._categorize_keyword(keyword),
            score=TrendScore(
                current_score=min(float(score), 100.0),
                peak_score=min(float(score) * 1.15, 100.0),
                growth_rate=random.uniform(-8.0, 18.0)
            ),
            platform_metrics=[PlatformMetrics(
                source=TrendSource.INSTAGRAM,
                engagement_score=engagement_score or min(float(score), 100.0),
                view_count=view_count,
                post_count=post_count,
                share_count=share_count,
                last_updated=datetime.now()
            )],
            regional_data=[RegionalData(
                country=geo,
                score=min(float(score), 100.0)
            )],
            related_keywords=self._generate_instagram_related_hashtags(keyword),
            first_detected=datetime.now(),
            last_updated=datetime.now(),
            is_rising=score > 65  # Instagram trends can be more volatile
        )
    
    def _categorize_keyword(self, keyword: str) -> TrendCategory:
        """Categorize a keyword into appropriate TrendCategory"""
        keyword_lower = keyword.lower()
        
        category_mapping = {
            TrendCategory.VIRAL_RECIPES: ['viral', 'trending', 'famous', 'popular', 'instagram', 'instafood'],
            TrendCategory.HEALTHY_EATING: ['healthy', 'clean', 'wellness', 'nutrition', 'superfood', 'organic'],
            TrendCategory.DESSERTS: ['dessert', 'sweet', 'cake', 'cookie', 'chocolate', 'treat'],
            TrendCategory.QUICK_MEALS: ['quick', 'easy', 'fast', 'simple', 'instant'],
            TrendCategory.COMFORT_FOOD: ['comfort', 'cozy', 'hearty', 'traditional', 'homestyle'],
            TrendCategory.INTERNATIONAL: ['asian', 'italian', 'mexican', 'mediterranean', 'fusion'],
            TrendCategory.COOKING_TECHNIQUES: ['cooking', 'technique', 'method', 'style', 'preparation'],
            TrendCategory.INGREDIENTS: ['fresh', 'organic', 'local', 'seasonal', 'ingredient']
        }
        
        for category, terms in category_mapping.items():
            if any(term in keyword_lower for term in terms):
                return category
        
        return TrendCategory.VIRAL_RECIPES  # Default for Instagram content