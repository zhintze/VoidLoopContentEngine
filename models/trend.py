from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from datetime import datetime
from enum import Enum


class TrendSource(str, Enum):
    """Source platforms for trend data"""
    GOOGLE_TRENDS = "google_trends"
    TIKTOK = "tiktok"
    PINTEREST = "pinterest" 
    REDDIT = "reddit"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"


class TrendCategory(str, Enum):
    """Food/recipe trend categories"""
    COMFORT_FOOD = "comfort_food"
    HEALTHY_EATING = "healthy_eating"
    INTERNATIONAL = "international"
    DESSERTS = "desserts"
    QUICK_MEALS = "quick_meals"
    DIETARY_RESTRICTIONS = "dietary_restrictions"
    SEASONAL = "seasonal"
    VIRAL_RECIPES = "viral_recipes"
    COOKING_TECHNIQUES = "cooking_techniques"
    INGREDIENTS = "ingredients"
    BEVERAGES = "beverages"


class TrendScore(BaseModel):
    """Trend popularity scoring"""
    current_score: float = Field(..., ge=0, le=100, description="Current trend score (0-100)")
    peak_score: float = Field(..., ge=0, le=100, description="Peak trend score reached")
    growth_rate: float = Field(..., description="Rate of growth (positive or negative)")
    velocity: Optional[float] = Field(None, description="Speed of trend change")
    momentum: Optional[float] = Field(None, description="Trend momentum indicator")


class RegionalData(BaseModel):
    """Regional trend performance"""
    country: str
    region: Optional[str] = None
    score: float = Field(..., ge=0, le=100)
    rank: Optional[int] = None


class PlatformMetrics(BaseModel):
    """Platform-specific trend metrics"""
    source: TrendSource
    engagement_score: float = Field(..., ge=0, le=100)
    post_count: Optional[int] = None
    view_count: Optional[int] = None
    share_count: Optional[int] = None
    comment_count: Optional[int] = None
    hashtag_usage: Optional[int] = None
    last_updated: datetime


class TrendKeyword(BaseModel):
    """Individual trending keyword/phrase"""
    model_config = {"extra": "allow"}  # Allow extra fields for dynamic attributes
    
    keyword: str
    category: TrendCategory
    score: TrendScore
    regional_data: List[RegionalData] = Field(default_factory=list)
    platform_metrics: List[PlatformMetrics] = Field(default_factory=list)
    related_keywords: List[str] = Field(default_factory=list)
    search_volume: Optional[int] = None
    competition_level: Optional[str] = Field(None, description="Low, Medium, High")
    seasonality: Optional[Dict[str, float]] = Field(default_factory=dict, description="Month -> score mapping")
    first_detected: datetime
    last_updated: datetime
    is_rising: bool = Field(default=True, description="Whether trend is currently rising")
    estimated_peak: Optional[datetime] = Field(None, description="Predicted peak date")


class TrendReport(BaseModel):
    """Comprehensive trend analysis report"""
    report_id: str
    generated_at: datetime
    time_period: str = Field(..., description="e.g., 'last_7_days', 'last_30_days'")
    
    # Top trends by category
    top_keywords: List[TrendKeyword] = Field(default_factory=list)
    rising_trends: List[TrendKeyword] = Field(default_factory=list)
    declining_trends: List[TrendKeyword] = Field(default_factory=list)
    
    # Analysis summaries
    category_breakdown: Dict[TrendCategory, int] = Field(default_factory=dict)
    platform_performance: Dict[TrendSource, float] = Field(default_factory=dict)
    regional_hotspots: List[RegionalData] = Field(default_factory=list)
    
    # Insights
    key_insights: List[str] = Field(default_factory=list)
    recommended_keywords: List[str] = Field(default_factory=list)
    content_opportunities: List[str] = Field(default_factory=list)


class AccountTrendProfile(BaseModel):
    """Account-specific trend preferences and performance"""
    account_id: str
    
    # Preferences
    preferred_categories: List[TrendCategory] = Field(default_factory=list)
    excluded_keywords: List[str] = Field(default_factory=list)
    target_regions: List[str] = Field(default_factory=list)
    min_trend_score: float = Field(default=20.0, ge=0, le=100)
    
    # Historical performance
    successful_trends: List[str] = Field(default_factory=list, description="Keywords that performed well")
    trend_adoption_rate: Optional[float] = Field(None, description="How quickly account adopts trends")
    preferred_platforms: List[TrendSource] = Field(default_factory=list)
    
    # Current tracking
    watching_keywords: List[str] = Field(default_factory=list)
    last_trend_update: Optional[datetime] = None
    
    def add_successful_trend(self, keyword: str):
        """Add a keyword that performed well"""
        if keyword not in self.successful_trends:
            self.successful_trends.append(keyword)
    
    def is_keyword_relevant(self, keyword: TrendKeyword) -> bool:
        """Check if a trend keyword is relevant for this account"""
        # Check excluded keywords
        if keyword.keyword.lower() in [k.lower() for k in self.excluded_keywords]:
            return False
            
        # Check minimum score
        if keyword.score.current_score < self.min_trend_score:
            return False
            
        # Check category preferences
        if self.preferred_categories and keyword.category not in self.preferred_categories:
            return False
            
        return True


class TrendDatabase(BaseModel):
    """In-memory trend database structure"""
    keywords: Dict[str, TrendKeyword] = Field(default_factory=dict)
    reports: List[TrendReport] = Field(default_factory=list)
    account_profiles: Dict[str, AccountTrendProfile] = Field(default_factory=dict)
    last_scan: Optional[datetime] = None
    
    def add_keyword(self, keyword: TrendKeyword):
        """Add or update a trend keyword"""
        self.keywords[keyword.keyword] = keyword
    
    def get_trending_by_category(self, category: TrendCategory, limit: int = 10) -> List[TrendKeyword]:
        """Get top trending keywords for a category"""
        category_trends = [k for k in self.keywords.values() if k.category == category]
        return sorted(category_trends, key=lambda x: x.score.current_score, reverse=True)[:limit]
    
    def get_account_recommendations(self, account_id: str, limit: int = 5) -> List[TrendKeyword]:
        """Get trend recommendations for a specific account"""
        if account_id not in self.account_profiles:
            return list(self.keywords.values())[:limit]
            
        profile = self.account_profiles[account_id]
        relevant_trends = [k for k in self.keywords.values() if profile.is_keyword_relevant(k)]
        return sorted(relevant_trends, key=lambda x: x.score.current_score, reverse=True)[:limit]