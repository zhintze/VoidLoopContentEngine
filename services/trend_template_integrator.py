from typing import List, Dict, Optional, Any
from datetime import datetime
import random
import re

from models.trend import TrendKeyword, TrendCategory
from services.trend_analyzer import TrendAnalyzer
from services.trend_filter import RecipeTrendFilter


class TrendTemplateIntegrator:
    """Integrates trend data with content templates for trend-driven content generation"""
    
    def __init__(self):
        self.trend_analyzer = TrendAnalyzer()
        self.trend_filter = RecipeTrendFilter()
        
        # Platform-specific trend keyword limits
        self.platform_limits = {
            'twitter': 3,     # Twitter has character limits
            'instagram': 5,   # Instagram allows more hashtags
            'pinterest': 4,   # Pinterest focuses on searchability
            'facebook': 4     # Facebook balanced approach
        }
        
        # Tone mappings for different trend types
        self.tone_mappings = {
            'viral': ['exciting', 'energetic', 'enthusiastic', 'buzz-worthy'],
            'trending': ['engaging', 'popular', 'current', 'fresh'],
            'emerging': ['innovative', 'cutting-edge', 'new', 'discovering'],
            'seasonal': ['timely', 'seasonal', 'perfect-timing', 'festive']
        }
    
    def enhance_template_context(self, base_context: Dict[str, Any], 
                                platform: str = 'instagram',
                                trend_preferences: Optional[Dict] = None) -> Dict[str, Any]:
        """Enhance template context with relevant trend data
        
        Args:
            base_context: Base template context
            platform: Target platform for content
            trend_preferences: Optional trend filtering preferences
            
        Returns:
            Enhanced context with trend data
        """
        # Get relevant trends based on preferences
        trends = self._get_relevant_trends(platform, trend_preferences)
        
        if not trends:
            # Return base context if no trends available
            return base_context
        
        # Select best trends for this platform
        selected_trends = self._select_platform_trends(trends, platform)
        
        # Create trend-enhanced context
        enhanced_context = base_context.copy()
        
        # Add trend-specific keywords
        trend_keywords = [trend.keyword for trend in selected_trends]
        enhanced_context.setdefault('keywords', []).extend(trend_keywords[:3])
        
        # Add trend-based hashtags
        trend_hashtags = self._generate_trend_hashtags(selected_trends, platform)
        enhanced_context.setdefault('hashtags', []).extend(trend_hashtags)
        
        # Adjust tone based on trending topics
        if selected_trends:
            trend_tone = self._suggest_tone_for_trends(selected_trends)
            enhanced_context['tone'] = trend_tone
        
        # Add trend insights for content creation
        enhanced_context['trend_insights'] = {
            'trending_keywords': [t.keyword for t in selected_trends],
            'categories': list(set(t.category.value for t in selected_trends)),
            'growth_potential': [
                {'keyword': t.keyword, 'growth_rate': t.score.growth_rate}
                for t in selected_trends if t.score.growth_rate > 0
            ],
            'viral_potential': [
                {'keyword': t.keyword, 'score': t.score.current_score}
                for t in selected_trends if t.score.current_score > 70
            ]
        }
        
        # Add trend-driven content suggestions
        enhanced_context['content_suggestions'] = self._generate_trend_content_suggestions(
            selected_trends, platform
        )
        
        return enhanced_context
    
    def generate_trending_variations(self, base_template: str, 
                                   trends: List[TrendKeyword],
                                   variations: int = 3) -> List[str]:
        """Generate multiple variations of content using different trends
        
        Args:
            base_template: Base template string
            trends: Available trends to use
            variations: Number of variations to generate
            
        Returns:
            List of template variations with different trend focuses
        """
        variations_list = []
        
        # Ensure we don't exceed available trends
        num_variations = min(variations, len(trends))
        
        for i in range(num_variations):
            # Select different trend focus for each variation
            primary_trend = trends[i % len(trends)]
            secondary_trends = [t for t in trends if t != primary_trend][:2]
            
            # Create variation-specific context
            variation_context = {
                'primary_keyword': primary_trend.keyword,
                'secondary_keywords': [t.keyword for t in secondary_trends],
                'trend_category': primary_trend.category.value.replace('_', ' ').title(),
                'growth_indicator': '📈' if primary_trend.is_rising else '📊',
                'engagement_boost': self._calculate_engagement_potential(primary_trend)
            }
            
            # Apply variation context to template
            customized_template = self._apply_variation_context(
                base_template, variation_context
            )
            variations_list.append(customized_template)
        
        return variations_list
    
    def optimize_hashtags_for_trends(self, base_hashtags: List[str],
                                   trends: List[TrendKeyword],
                                   platform: str,
                                   max_hashtags: int = None) -> List[str]:
        """Optimize hashtags by incorporating trending keywords
        
        Args:
            base_hashtags: Original hashtags
            trends: Available trends
            platform: Target platform
            max_hashtags: Maximum number of hashtags
            
        Returns:
            Optimized hashtag list
        """
        # Get platform-specific limits
        if max_hashtags is None:
            max_hashtags = {
                'twitter': 2,      # Keep minimal for character count
                'instagram': 10,   # Instagram allows up to 30, but 10 is optimal
                'pinterest': 8,    # Pinterest focuses on searchability
                'facebook': 5      # Facebook prefers fewer hashtags
            }.get(platform, 5)
        
        optimized_hashtags = base_hashtags.copy()
        
        # Add trending hashtags
        trend_hashtags = []
        for trend in trends[:5]:  # Limit to top 5 trends
            # Convert trend keyword to hashtag format
            hashtag = self._keyword_to_hashtag(trend.keyword)
            if hashtag and hashtag not in optimized_hashtags:
                trend_hashtags.append(hashtag)
        
        # Prioritize trend hashtags based on scores
        trend_hashtags.sort(
            key=lambda h: next(
                (t.score.current_score for t in trends 
                 if self._keyword_to_hashtag(t.keyword) == h), 0
            ),
            reverse=True
        )
        
        # Combine and limit
        optimized_hashtags.extend(trend_hashtags)
        
        return optimized_hashtags[:max_hashtags]
    
    def suggest_content_timing(self, trends: List[TrendKeyword]) -> Dict[str, Any]:
        """Suggest optimal timing for content based on trend analysis
        
        Args:
            trends: List of trends to analyze
            
        Returns:
            Timing recommendations
        """
        if not trends:
            return {'recommendation': 'No trend data available'}
        
        # Analyze trend momentum
        rising_trends = [t for t in trends if t.is_rising and t.score.growth_rate > 5]
        peak_trends = [t for t in trends if t.score.current_score > 70]
        
        timing_advice = {
            'urgency_level': 'low',
            'recommendation': 'Standard posting schedule',
            'reasoning': '',
            'optimal_window': '24-48 hours'
        }
        
        if rising_trends:
            fastest_rising = max(rising_trends, key=lambda x: x.score.growth_rate)
            timing_advice.update({
                'urgency_level': 'high',
                'recommendation': 'Post immediately to catch rising trend',
                'reasoning': f"'{fastest_rising.keyword}' is rising rapidly ({fastest_rising.score.growth_rate:.1f}% growth)",
                'optimal_window': '6-12 hours'
            })
        elif peak_trends:
            top_trend = max(peak_trends, key=lambda x: x.score.current_score)
            timing_advice.update({
                'urgency_level': 'medium',
                'recommendation': 'Post soon while trend is hot',
                'reasoning': f"'{top_trend.keyword}' is at peak performance ({top_trend.score.current_score:.1f} score)",
                'optimal_window': '12-24 hours'
            })
        
        return timing_advice
    
    def _get_relevant_trends(self, platform: str, 
                           preferences: Optional[Dict] = None) -> List[TrendKeyword]:
        """Get relevant trends based on platform and preferences"""
        # This would typically fetch from TrendStorage/TrendService
        # For now, return mock data to demonstrate integration
        
        from models.trend import TrendScore, PlatformMetrics, TrendSource
        from datetime import datetime
        
        mock_trends = [
            TrendKeyword(
                keyword="air fryer recipes",
                category=TrendCategory.COOKING_TECHNIQUES,
                score=TrendScore(current_score=85.0, peak_score=90.0, growth_rate=12.5),
                platform_metrics=[PlatformMetrics(
                    source=TrendSource.GOOGLE_TRENDS,
                    engagement_score=85.0,
                    last_updated=datetime.now()
                )],
                first_detected=datetime.now(),
                last_updated=datetime.now(),
                is_rising=True
            ),
            TrendKeyword(
                keyword="healthy meal prep",
                category=TrendCategory.HEALTHY_EATING,
                score=TrendScore(current_score=72.0, peak_score=75.0, growth_rate=8.2),
                platform_metrics=[PlatformMetrics(
                    source=TrendSource.INSTAGRAM,
                    engagement_score=72.0,
                    last_updated=datetime.now()
                )],
                first_detected=datetime.now(),
                last_updated=datetime.now(),
                is_rising=True
            )
        ]
        
        # Apply preferences filtering if provided
        if preferences:
            if 'categories' in preferences:
                preferred_categories = preferences['categories']
                mock_trends = [t for t in mock_trends if t.category in preferred_categories]
            
            if 'min_score' in preferences:
                min_score = preferences['min_score']
                mock_trends = [t for t in mock_trends if t.score.current_score >= min_score]
        
        return mock_trends
    
    def _select_platform_trends(self, trends: List[TrendKeyword], 
                              platform: str) -> List[TrendKeyword]:
        """Select the best trends for a specific platform"""
        # Limit based on platform constraints
        max_trends = self.platform_limits.get(platform, 4)
        
        # Score trends for this platform
        platform_scores = []
        for trend in trends:
            base_score = self.trend_analyzer.calculate_composite_score(trend)
            
            # Platform-specific adjustments
            platform_bonus = 0
            for metric in trend.platform_metrics:
                if self._source_matches_platform(metric.source, platform):
                    platform_bonus += 10  # Bonus for platform presence
            
            total_score = base_score + platform_bonus
            platform_scores.append((trend, total_score))
        
        # Sort by platform-adjusted score
        platform_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [trend for trend, score in platform_scores[:max_trends]]
    
    def _generate_trend_hashtags(self, trends: List[TrendKeyword], 
                               platform: str) -> List[str]:
        """Generate hashtags from trending keywords"""
        hashtags = []
        
        for trend in trends:
            # Convert keyword to hashtag
            hashtag = self._keyword_to_hashtag(trend.keyword)
            if hashtag:
                hashtags.append(hashtag)
            
            # Add category hashtag
            category_hashtag = f"#{trend.category.value}"
            if category_hashtag not in hashtags:
                hashtags.append(category_hashtag)
        
        return hashtags[:self.platform_limits.get(platform, 4)]
    
    def _suggest_tone_for_trends(self, trends: List[TrendKeyword]) -> str:
        """Suggest appropriate tone based on trend characteristics"""
        # Analyze trend types
        trend_types = []
        for trend in trends:
            trend_type = self.trend_analyzer.classify_trend_type(trend)
            trend_types.append(trend_type)
        
        # Determine dominant trend type
        if 'viral' in trend_types:
            return random.choice(self.tone_mappings['viral'])
        elif 'trending' in trend_types:
            return random.choice(self.tone_mappings['trending'])
        elif any(t.category == TrendCategory.SEASONAL for t in trends):
            return random.choice(self.tone_mappings['seasonal'])
        else:
            return random.choice(self.tone_mappings['emerging'])
    
    def _generate_trend_content_suggestions(self, trends: List[TrendKeyword],
                                          platform: str) -> List[str]:
        """Generate content suggestions based on trends"""
        suggestions = []
        
        for trend in trends[:3]:  # Top 3 trends
            keyword = trend.keyword
            category = trend.category.value.replace('_', ' ')
            
            if platform == 'instagram':
                suggestions.append(f"Create a Reel showcasing {keyword} step-by-step")
                suggestions.append(f"Share {category} tips with {keyword} focus")
            elif platform == 'tiktok':
                suggestions.append(f"Film quick {keyword} hack or tip")
                suggestions.append(f"Join {keyword} trend with unique twist")
            elif platform == 'pinterest':
                suggestions.append(f"Design infographic for {keyword} benefits")
                suggestions.append(f"Create recipe card collection for {keyword}")
            else:  # General suggestions
                suggestions.append(f"Share {keyword} recipe with personal story")
                suggestions.append(f"Highlight {keyword} health benefits")
        
        return suggestions
    
    def _calculate_engagement_potential(self, trend: TrendKeyword) -> str:
        """Calculate engagement potential description"""
        score = trend.score.current_score
        growth = trend.score.growth_rate
        
        if score > 80 and growth > 10:
            return "Very High"
        elif score > 60 and growth > 5:
            return "High"
        elif score > 40:
            return "Medium"
        else:
            return "Low"
    
    def _apply_variation_context(self, template: str, context: Dict) -> str:
        """Apply variation-specific context to template"""
        # Simple template variable replacement
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in template:
                template = template.replace(placeholder, str(value))
        
        return template
    
    def _keyword_to_hashtag(self, keyword: str) -> str:
        """Convert keyword to hashtag format"""
        # Clean and format keyword as hashtag
        cleaned = re.sub(r'[^\w\s]', '', keyword)  # Remove special chars
        hashtag = '#' + ''.join(word.capitalize() for word in cleaned.split())
        
        # Ensure it's not too long
        if len(hashtag) > 30:
            hashtag = hashtag[:30]
        
        return hashtag
    
    def _source_matches_platform(self, source: Any, platform: str) -> bool:
        """Check if trend source matches target platform"""
        source_str = str(source).lower()
        platform_lower = platform.lower()
        
        # Map trend sources to platforms
        platform_mapping = {
            'instagram': ['instagram'],
            'tiktok': ['tiktok'],
            'pinterest': ['pinterest'],
            'facebook': ['facebook'],
            'twitter': ['twitter']
        }
        
        return any(source_match in source_str 
                  for source_match in platform_mapping.get(platform_lower, []))