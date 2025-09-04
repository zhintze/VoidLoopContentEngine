from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
import asyncio
import time

from services.reddit_trends import RedditTrendsService
from services.tiktok_trends import TikTokTrendsService
from services.pinterest_trends import PinterestTrendsService
from services.instagram_trends import InstagramTrendsService
from services.trend_service import TrendService
from services.theme_trend_integration import theme_trend_integrator
from models.trend import TrendKeyword, TrendCategory, TrendSource
from models.trend_storage import TrendStorage


class TrendScraper:
    """Main trend scraping coordinator that combines multiple sources"""
    
    def __init__(self, data_dir: str = "data/trends", theme_id: str = "food_recipe_general"):
        self.reddit_trends = RedditTrendsService()
        self.tiktok_trends = TikTokTrendsService()
        self.pinterest_trends = PinterestTrendsService()
        self.instagram_trends = InstagramTrendsService()
        self.trend_service = TrendService(data_dir)
        self.trend_storage = TrendStorage()
        
        # Theme system integration
        self.theme_id = theme_id
        self.theme_integrator = theme_trend_integrator
        
        # Tracking for rate limiting and deduplication
        self.last_scrape_time = {}
        self.scraped_keywords: Set[str] = set()
    
    @property
    def seed_keywords(self) -> List[str]:
        """Get seed keywords from theme system"""
        return self.theme_integrator.get_theme_based_seed_keywords(self.theme_id)
    
    def scrape_all_trends(self, geo: str = 'US', 
                         timeframe: str = 'today 7-d',
                         max_keywords: int = 100) -> Dict[str, List[TrendKeyword]]:
        """Scrape trends from all available sources
        
        Args:
            geo: Geographic location for trends
            timeframe: Time range for trends
            max_keywords: Maximum keywords to collect
            
        Returns:
            Dict with source names as keys and trend lists as values
        """
        all_trends = {}
        
        print(f"Starting trend scraping for {geo} - {timeframe}")
        
        # 1. Get trending food topics from Reddit
        print("Fetching trending food topics from Reddit...")
        reddit_trending = self.reddit_trends.get_trending_food_topics(
            geo=geo, 
            timeframe=timeframe, 
            limit=20
        )
        all_trends['reddit_trending'] = reddit_trending
        self._save_trends_to_storage(reddit_trending)
        
        # 2. Get trending hashtags from TikTok
        print("Fetching trending food hashtags from TikTok...")
        tiktok_trends = self.tiktok_trends.get_trending_food_hashtags(
            geo=geo,
            limit=15
        )
        all_trends['tiktok_trends'] = tiktok_trends
        self._save_trends_to_storage(tiktok_trends)
        
        # 3. Get trending pins from Pinterest
        print("Fetching trending food pins from Pinterest...")
        pinterest_trends = self.pinterest_trends.get_trending_food_pins(
            geo=geo,
            limit=15
        )
        all_trends['pinterest_trends'] = pinterest_trends
        self._save_trends_to_storage(pinterest_trends)
        
        # 4. Get trending hashtags from Instagram
        print("Fetching trending food hashtags from Instagram...")
        instagram_trends = self.instagram_trends.get_trending_food_hashtags(
            geo=geo,
            limit=15
        )
        all_trends['instagram_trends'] = instagram_trends
        self._save_trends_to_storage(instagram_trends)
        
        # 5. Search for specific recipe trends across platforms
        print("Searching seed keyword trends across platforms...")
        recipe_keywords = self.seed_keywords[:10]  # Limit for performance
        
        # Reddit recipe search
        reddit_recipes = self.reddit_trends.search_recipe_trends(
            keywords=recipe_keywords,
            geo=geo,
            timeframe=timeframe
        )
        all_trends['reddit_recipes'] = reddit_recipes
        self._save_trends_to_storage(reddit_recipes)
        
        # TikTok recipe search
        tiktok_recipes = self.tiktok_trends.search_recipe_trends(
            keywords=recipe_keywords,
            geo=geo,
            timeframe=timeframe
        )
        all_trends['tiktok_recipes'] = tiktok_recipes
        self._save_trends_to_storage(tiktok_recipes)
        
        # Pinterest recipe search
        pinterest_recipes = self.pinterest_trends.search_recipe_trends(
            keywords=recipe_keywords,
            geo=geo,
            timeframe=timeframe
        )
        all_trends['pinterest_recipes'] = pinterest_recipes
        self._save_trends_to_storage(pinterest_recipes)
        
        # Instagram recipe search
        instagram_recipes = self.instagram_trends.search_recipe_trends(
            keywords=recipe_keywords,
            geo=geo,
            timeframe=timeframe
        )
        all_trends['instagram_recipes'] = instagram_recipes
        self._save_trends_to_storage(instagram_recipes)
        
        # 6. Get seasonal trends
        print("Fetching seasonal trends...")
        seasonal_reddit = self.reddit_trends.get_seasonal_recipe_trends(geo=geo)
        seasonal_pinterest = self.pinterest_trends.get_seasonal_recipe_trends(geo=geo)
        
        all_trends['seasonal_reddit'] = seasonal_reddit
        all_trends['seasonal_pinterest'] = seasonal_pinterest
        self._save_trends_to_storage(seasonal_reddit + seasonal_pinterest)
        
        # 7. Get viral content
        print("Fetching viral food content...")
        tiktok_viral = self.tiktok_trends.get_viral_food_content(limit=10)
        instagram_visual = self.instagram_trends.get_visual_food_trends(limit=10)
        
        all_trends['tiktok_viral'] = tiktok_viral
        all_trends['instagram_visual'] = instagram_visual
        self._save_trends_to_storage(tiktok_viral + instagram_visual)
        
        # 8. Update trend database
        self._update_trend_database(all_trends)
        
        # Summary
        total_trends = sum(len(trends) for trends in all_trends.values())
        print(f"Scraping complete! Found {total_trends} trending keywords across {len(all_trends)} sources")
        
        return all_trends
    
    def scrape_trending_topics_only(self, geo: str = 'US', 
                                  limit: int = 50) -> List[TrendKeyword]:
        """Quick scrape of trending topics from all platforms"""
        print(f"Quick scraping trending topics across platforms for {geo}...")
        
        all_trending = []
        
        # Reddit trending (stable, text-based)
        reddit_trending = self.reddit_trends.get_trending_food_topics(
            geo=geo,
            timeframe='day',
            limit=limit//4
        )
        all_trending.extend(reddit_trending)
        
        # TikTok viral content (fast-moving trends)
        tiktok_viral = self.tiktok_trends.get_viral_food_content(limit=limit//4)
        all_trending.extend(tiktok_viral)
        
        # Instagram visual trends (high engagement)
        instagram_visual = self.instagram_trends.get_visual_food_trends(limit=limit//4)
        all_trending.extend(instagram_visual)
        
        # Pinterest seasonal (planning ahead)
        pinterest_seasonal = self.pinterest_trends.get_seasonal_recipe_trends(geo=geo)
        all_trending.extend(pinterest_seasonal[:limit//4])
        
        # Save and update trends
        self._save_trends_to_storage(all_trending)
        
        # Update existing keywords with new scores
        for trend in all_trending:
            existing = self.trend_storage.get_trend_keyword(trend.keyword)
            if existing:
                # Update score but keep historical data
                source_map = {
                    'reddit': TrendSource.REDDIT,
                    'tiktok': TrendSource.TIKTOK,
                    'pinterest': TrendSource.PINTEREST,
                    'instagram': TrendSource.INSTAGRAM
                }
                source = trend.platform_metrics[0].source if trend.platform_metrics else TrendSource.REDDIT
                
                self.trend_service.update_trend_score(
                    keyword=trend.keyword,
                    new_score=trend.score.current_score,
                    source=source
                )
            else:
                # Add new trend
                self.trend_storage.save_trend_keyword(trend)
        
        print(f"Updated {len(all_trending)} trending topics from {len(set(t.platform_metrics[0].source for t in all_trending if t.platform_metrics))} platforms")
        return all_trending[:limit]
    
    def scrape_by_category(self, category: TrendCategory, 
                          geo: str = 'US', 
                          limit: int = 20) -> List[TrendKeyword]:
        """Scrape trends for a specific food category across all platforms"""
        print(f"Scraping trends for category: {category.value}")
        
        all_category_trends = []
        
        # Get category-specific keywords
        category_keywords = self._get_category_keywords(category)
        
        # Search across all platforms
        reddit_trends = self.reddit_trends.search_recipe_trends(
            keywords=category_keywords[:5],
            geo=geo,
            timeframe='week'
        )
        all_category_trends.extend(reddit_trends)
        
        # TikTok category trends
        tiktok_trends = self.tiktok_trends.search_recipe_trends(
            keywords=category_keywords[:5],
            geo=geo,
            timeframe='week'
        )
        all_category_trends.extend(tiktok_trends)
        
        # Pinterest category-specific trends
        pinterest_category_trends = self.pinterest_trends.get_pinterest_food_trends_by_category(
            category=category,
            limit=limit//4
        )
        all_category_trends.extend(pinterest_category_trends)
        
        # Instagram category search
        instagram_trends = self.instagram_trends.search_recipe_trends(
            keywords=category_keywords[:5],
            geo=geo,
            timeframe='week'
        )
        all_category_trends.extend(instagram_trends)
        
        # Filter and enhance trends for the category
        category_trends = []
        for trend in all_category_trends:
            if trend.category == category or self._matches_category(trend.keyword, category):
                trend.category = category  # Ensure correct category
                category_trends.append(trend)
        
        # Sort by score and remove duplicates
        unique_trends = {}
        for trend in category_trends:
            if trend.keyword not in unique_trends or trend.score.current_score > unique_trends[trend.keyword].score.current_score:
                unique_trends[trend.keyword] = trend
        
        final_trends = sorted(unique_trends.values(), key=lambda x: x.score.current_score, reverse=True)
        
        self._save_trends_to_storage(final_trends)
        
        print(f"Found {len(final_trends)} trends for {category.value} across all platforms")
        return final_trends[:limit]
    
    def get_trend_summary(self) -> Dict:
        """Get a summary of current trend data"""
        stats = self.trend_storage.get_database_stats()
        
        # Get top trending keywords
        top_trends = self.trend_storage.get_trending_keywords(limit=10)
        rising_trends = self.trend_storage.get_rising_trends(hours=24, limit=10)
        
        summary = {
            'database_stats': stats,
            'top_keywords': [t.keyword for t in top_trends],
            'rising_keywords': [t.keyword for t in rising_trends],
            'last_scrape': datetime.now().isoformat(),
            'categories_tracked': len(set(t.category for t in top_trends + rising_trends))
        }
        
        return summary
    
    def _save_trends_to_storage(self, trends: List[TrendKeyword]):
        """Save trends to both storage systems"""
        for trend in trends:
            # Skip duplicates
            if trend.keyword.lower() not in self.scraped_keywords:
                self.trend_storage.save_trend_keyword(trend)
                self.scraped_keywords.add(trend.keyword.lower())
    
    def _extract_related_keywords(self, trends: List[TrendKeyword]) -> List[str]:
        """Extract related keywords from scraped trends"""
        related = set()
        
        for trend in trends:
            # Add related keywords from the trend object
            for related_kw in trend.related_keywords:
                if self._is_food_related(related_kw) and related_kw not in self.scraped_keywords:
                    related.add(related_kw)
        
        return list(related)[:20]  # Limit to prevent overload
    
    def _update_trend_database(self, all_trends: Dict[str, List[TrendKeyword]]):
        """Update the trend service database with new data"""
        for source, trends in all_trends.items():
            for trend in trends:
                # Check if trend exists
                existing = self.trend_service.database.keywords.get(trend.keyword)
                
                if existing:
                    # Update existing trend score
                    self.trend_service.update_trend_score(
                        keyword=trend.keyword,
                        new_score=trend.score.current_score,
                        source=TrendSource.REDDIT
                    )
                else:
                    # Add new trend to service
                    self.trend_service.database.keywords[trend.keyword] = trend
        
        # Save the updated database
        self.trend_service._save_database()
    
    def _get_category_keywords(self, category: TrendCategory) -> List[str]:
        """Get keywords specific to a trend category"""
        category_keywords = {
            TrendCategory.COMFORT_FOOD: [
                'mac and cheese', 'fried chicken', 'pizza recipes', 'burger recipes',
                'grilled cheese', 'meatloaf', 'chicken pot pie', 'shepherd pie'
            ],
            TrendCategory.HEALTHY_EATING: [
                'green smoothies', 'quinoa recipes', 'kale salad', 'chia pudding',
                'protein bowls', 'superfood recipes', 'clean eating', 'detox recipes'
            ],
            TrendCategory.QUICK_MEALS: [
                '15 minute meals', '30 minute dinners', 'instant pot recipes',
                'microwave recipes', 'no cook meals', 'one pot pasta'
            ],
            TrendCategory.DESSERTS: [
                'chocolate cake', 'cookies', 'ice cream recipes', 'cheesecake',
                'brownies', 'cupcakes', 'pie recipes', 'dessert bars'
            ],
            TrendCategory.INTERNATIONAL: [
                'pasta recipes', 'curry recipes', 'tacos', 'stir fry',
                'ramen recipes', 'thai food', 'indian recipes', 'mexican food'
            ]
        }
        
        return category_keywords.get(category, self.seed_keywords[:10])
    
    def _matches_category(self, keyword: str, category: TrendCategory) -> bool:
        """Check if a keyword matches a specific category"""
        keyword_lower = keyword.lower()
        
        category_terms = {
            TrendCategory.COMFORT_FOOD: ['comfort', 'fried', 'creamy', 'hearty', 'classic'],
            TrendCategory.HEALTHY_EATING: ['healthy', 'nutritious', 'clean', 'superfood', 'green'],
            TrendCategory.QUICK_MEALS: ['quick', 'easy', 'fast', 'instant', 'minute'],
            TrendCategory.DESSERTS: ['sweet', 'dessert', 'cake', 'cookie', 'chocolate'],
            TrendCategory.INTERNATIONAL: ['asian', 'italian', 'mexican', 'indian', 'thai']
        }
        
        terms = category_terms.get(category, [])
        return any(term in keyword_lower for term in terms)
    
    def _is_food_related(self, keyword: str) -> bool:
        """Check if keyword is food-related"""
        return self.reddit_trends._is_food_related(keyword)
    
    def cleanup_old_trends(self, days: int = 30):
        """Clean up old trend data from storage"""
        removed_count = self.trend_storage.cleanup_old_data(days)
        self.trend_service.cleanup_old_trends(days)
        
        print(f"Cleaned up {removed_count} old trend records")
        return removed_count