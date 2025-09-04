from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
from pathlib import Path
import uuid

from models.trend import (
    TrendKeyword, TrendReport, AccountTrendProfile, TrendDatabase,
    TrendSource, TrendCategory, TrendScore, PlatformMetrics, RegionalData
)


class TrendService:
    """Service for managing trend data and analysis"""
    
    def __init__(self, data_dir: str = "data/trends"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_file = self.data_dir / "trend_database.json"
        self.database = self._load_database()
    
    def _load_database(self) -> TrendDatabase:
        """Load trend database from disk"""
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    return TrendDatabase(**data)
            except Exception as e:
                print(f"Error loading trend database: {e}")
                return TrendDatabase()
        return TrendDatabase()
    
    def _save_database(self):
        """Save trend database to disk"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.database.model_dump(mode='json'), f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving trend database: {e}")
    
    def add_trend_keyword(self, keyword: str, category: TrendCategory, 
                         current_score: float, source: TrendSource,
                         **kwargs) -> TrendKeyword:
        """Add a new trend keyword"""
        now = datetime.now()
        
        # Create trend score
        score = TrendScore(
            current_score=current_score,
            peak_score=kwargs.get('peak_score', current_score),
            growth_rate=kwargs.get('growth_rate', 0.0)
        )
        
        # Create platform metrics
        platform_metrics = [PlatformMetrics(
            source=source,
            engagement_score=current_score,
            post_count=kwargs.get('post_count'),
            view_count=kwargs.get('view_count'),
            last_updated=now
        )]
        
        # Create trend keyword
        trend = TrendKeyword(
            keyword=keyword,
            category=category,
            score=score,
            platform_metrics=platform_metrics,
            related_keywords=kwargs.get('related_keywords', []),
            search_volume=kwargs.get('search_volume'),
            competition_level=kwargs.get('competition_level'),
            first_detected=now,
            last_updated=now,
            is_rising=kwargs.get('is_rising', True)
        )
        
        # Add to database
        self.database.add_keyword(trend)
        self._save_database()
        
        return trend
    
    def update_trend_score(self, keyword: str, new_score: float, source: TrendSource):
        """Update the score for an existing trend"""
        if keyword in self.database.keywords:
            trend = self.database.keywords[keyword]
            old_score = trend.score.current_score
            
            # Update score
            trend.score.current_score = new_score
            trend.score.growth_rate = new_score - old_score
            trend.score.peak_score = max(trend.score.peak_score, new_score)
            trend.is_rising = new_score > old_score
            trend.last_updated = datetime.now()
            
            # Update platform metrics
            for metric in trend.platform_metrics:
                if metric.source == source:
                    metric.engagement_score = new_score
                    metric.last_updated = datetime.now()
                    break
            
            self._save_database()
    
    def get_trending_keywords(self, category: Optional[TrendCategory] = None,
                            source: Optional[TrendSource] = None,
                            min_score: float = 0.0,
                            limit: int = 20) -> List[TrendKeyword]:
        """Get trending keywords with filters"""
        keywords = list(self.database.keywords.values())
        
        # Apply filters
        if category:
            keywords = [k for k in keywords if k.category == category]
        
        if source:
            keywords = [k for k in keywords if any(m.source == source for m in k.platform_metrics)]
        
        if min_score > 0:
            keywords = [k for k in keywords if k.score.current_score >= min_score]
        
        # Sort by current score
        keywords.sort(key=lambda x: x.score.current_score, reverse=True)
        
        return keywords[:limit]
    
    def get_rising_trends(self, hours: int = 24, limit: int = 10) -> List[TrendKeyword]:
        """Get trends that are currently rising"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_trends = [
            k for k in self.database.keywords.values() 
            if k.last_updated >= cutoff and k.is_rising and k.score.growth_rate > 0
        ]
        
        # Sort by growth rate
        recent_trends.sort(key=lambda x: x.score.growth_rate, reverse=True)
        
        return recent_trends[:limit]
    
    def create_account_profile(self, account_id: str, 
                             preferred_categories: List[TrendCategory] = None,
                             target_regions: List[str] = None,
                             min_trend_score: float = 20.0) -> AccountTrendProfile:
        """Create a trend profile for an account"""
        profile = AccountTrendProfile(
            account_id=account_id,
            preferred_categories=preferred_categories or [],
            target_regions=target_regions or [],
            min_trend_score=min_trend_score
        )
        
        self.database.account_profiles[account_id] = profile
        self._save_database()
        
        return profile
    
    def get_account_recommendations(self, account_id: str, 
                                  limit: int = 5) -> List[TrendKeyword]:
        """Get personalized trend recommendations for an account"""
        return self.database.get_account_recommendations(account_id, limit)
    
    def generate_trend_report(self, time_period: str = "last_7_days") -> TrendReport:
        """Generate a comprehensive trend report"""
        now = datetime.now()
        report_id = str(uuid.uuid4())
        
        # Get time range
        if time_period == "last_7_days":
            cutoff = now - timedelta(days=7)
        elif time_period == "last_30_days":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = now - timedelta(days=1)
        
        # Filter recent trends
        recent_keywords = [
            k for k in self.database.keywords.values()
            if k.last_updated >= cutoff
        ]
        
        # Categorize trends
        top_keywords = sorted(recent_keywords, key=lambda x: x.score.current_score, reverse=True)[:10]
        rising_trends = [k for k in recent_keywords if k.is_rising and k.score.growth_rate > 0][:10]
        declining_trends = [k for k in recent_keywords if not k.is_rising and k.score.growth_rate < 0][:10]
        
        # Category breakdown
        category_breakdown = {}
        for keyword in recent_keywords:
            category = keyword.category
            category_breakdown[category] = category_breakdown.get(category, 0) + 1
        
        # Platform performance
        platform_performance = {}
        for keyword in recent_keywords:
            for metric in keyword.platform_metrics:
                source = metric.source
                if source not in platform_performance:
                    platform_performance[source] = []
                platform_performance[source].append(metric.engagement_score)
        
        # Average platform scores
        for source in platform_performance:
            scores = platform_performance[source]
            platform_performance[source] = sum(scores) / len(scores) if scores else 0
        
        # Generate insights
        insights = self._generate_insights(recent_keywords, rising_trends)
        
        # Content opportunities
        opportunities = self._generate_opportunities(rising_trends, top_keywords)
        
        report = TrendReport(
            report_id=report_id,
            generated_at=now,
            time_period=time_period,
            top_keywords=top_keywords,
            rising_trends=rising_trends,
            declining_trends=declining_trends,
            category_breakdown=category_breakdown,
            platform_performance=platform_performance,
            key_insights=insights,
            recommended_keywords=[k.keyword for k in rising_trends[:5]],
            content_opportunities=opportunities
        )
        
        # Save report
        self.database.reports.append(report)
        self._save_database()
        
        return report
    
    def _generate_insights(self, keywords: List[TrendKeyword], 
                          rising: List[TrendKeyword]) -> List[str]:
        """Generate trend insights"""
        insights = []
        
        if not keywords:
            return ["No trend data available for this period"]
        
        # Most popular category
        categories = {}
        for k in keywords:
            categories[k.category] = categories.get(k.category, 0) + 1
        
        if categories:
            top_category = max(categories, key=categories.get)
            insights.append(f"{top_category.value.replace('_', ' ').title()} is the most active trend category")
        
        # Rising trend analysis
        if rising:
            avg_growth = sum(k.score.growth_rate for k in rising) / len(rising)
            insights.append(f"Average growth rate for rising trends: {avg_growth:.1f} points")
            
            fastest_growing = max(rising, key=lambda x: x.score.growth_rate)
            insights.append(f"Fastest growing trend: '{fastest_growing.keyword}' (+{fastest_growing.score.growth_rate:.1f})")
        
        # Platform insights
        platform_counts = {}
        for k in keywords:
            for metric in k.platform_metrics:
                platform_counts[metric.source] = platform_counts.get(metric.source, 0) + 1
        
        if platform_counts:
            top_platform = max(platform_counts, key=platform_counts.get)
            insights.append(f"{top_platform.value.replace('_', ' ').title()} has the most trend activity")
        
        return insights
    
    def _generate_opportunities(self, rising: List[TrendKeyword], 
                              top: List[TrendKeyword]) -> List[str]:
        """Generate content opportunities"""
        opportunities = []
        
        # Rising trend opportunities
        for trend in rising[:3]:
            opportunities.append(
                f"Create content around '{trend.keyword}' - rising {trend.score.growth_rate:.1f} points"
            )
        
        # High-scoring opportunities
        for trend in top[:2]:
            if trend.score.current_score > 70:
                opportunities.append(
                    f"Leverage high-performing trend '{trend.keyword}' (Score: {trend.score.current_score:.1f})"
                )
        
        return opportunities
    
    def cleanup_old_trends(self, days: int = 30):
        """Remove trends older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        
        old_keywords = [
            k for k in self.database.keywords.keys()
            if self.database.keywords[k].last_updated < cutoff
        ]
        
        for keyword in old_keywords:
            del self.database.keywords[keyword]
        
        if old_keywords:
            print(f"Removed {len(old_keywords)} old trends")
            self._save_database()
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the trend database"""
        db = self.database
        
        return {
            "total_keywords": len(db.keywords),
            "total_reports": len(db.reports),
            "account_profiles": len(db.account_profiles),
            "last_scan": db.last_scan.isoformat() if db.last_scan else None,
            "categories": len(set(k.category for k in db.keywords.values())),
            "sources": len(set(
                metric.source 
                for k in db.keywords.values() 
                for metric in k.platform_metrics
            )),
            "avg_score": sum(k.score.current_score for k in db.keywords.values()) / len(db.keywords) if db.keywords else 0
        }