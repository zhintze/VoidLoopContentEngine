from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import statistics
import math
from collections import defaultdict

from models.trend import TrendKeyword, TrendCategory, TrendSource, TrendScore, TrendReport


class TrendAnalyzer:
    """Advanced trend analysis and scoring system"""
    
    def __init__(self):
        self.scoring_weights = {
            'current_score': 0.25,      # Current popularity
            'growth_rate': 0.30,        # Rate of growth
            'consistency': 0.20,        # Consistent performance
            'recency': 0.15,           # How recent the trend is
            'platform_diversity': 0.10 # Available across platforms
        }
        
        # Score thresholds for trend classification
        self.score_thresholds = {
            'viral': 80.0,        # Viral trends (very high score)
            'trending': 60.0,     # Trending (good score)  
            'emerging': 40.0,     # Emerging trends
            'declining': 20.0,    # Declining trends
            'niche': 10.0        # Niche/low interest
        }
    
    def analyze_trends(self, trends: List[TrendKeyword]) -> Dict:
        """Comprehensive analysis of trend data"""
        if not trends:
            return {'error': 'No trends to analyze'}
        
        analysis = {
            'total_trends': len(trends),
            'analyzed_at': datetime.now().isoformat(),
            'score_distribution': self._analyze_score_distribution(trends),
            'category_performance': self._analyze_category_performance(trends),
            'growth_analysis': self._analyze_growth_patterns(trends),
            'platform_analysis': self._analyze_platform_performance(trends),
            'temporal_analysis': self._analyze_temporal_patterns(trends),
            'top_performers': self._get_top_performers(trends),
            'recommendations': self._generate_recommendations(trends),
            'insights': self._generate_insights(trends)
        }
        
        return analysis
    
    def calculate_composite_score(self, trend: TrendKeyword) -> float:
        """Calculate a composite score for a trend based on multiple factors"""
        scores = {}
        
        # 1. Current Score (normalized)
        scores['current_score'] = min(trend.score.current_score / 100.0, 1.0)
        
        # 2. Growth Rate (normalized and clamped)
        growth_rate = trend.score.growth_rate
        # Normalize growth rate (-100 to +100) to (0 to 1)
        scores['growth_rate'] = max(0, min((growth_rate + 100) / 200, 1.0))
        
        # 3. Consistency Score (based on peak vs current)
        if trend.score.peak_score > 0:
            scores['consistency'] = trend.score.current_score / trend.score.peak_score
        else:
            scores['consistency'] = 0.5
        
        # 4. Recency Score (how recent the trend is)
        hours_old = (datetime.now() - trend.last_updated).total_seconds() / 3600
        scores['recency'] = max(0, 1.0 - (hours_old / 168))  # 1 week decay
        
        # 5. Platform Diversity Score
        platform_count = len(trend.platform_metrics)
        scores['platform_diversity'] = min(platform_count / 5.0, 1.0)  # Max 5 platforms
        
        # Calculate weighted composite score
        composite_score = sum(
            scores[factor] * weight 
            for factor, weight in self.scoring_weights.items() 
            if factor in scores
        )
        
        return composite_score * 100  # Return as percentage
    
    def classify_trend_type(self, trend: TrendKeyword) -> str:
        """Classify trend based on score and characteristics"""
        composite_score = self.calculate_composite_score(trend)
        
        for trend_type, threshold in sorted(self.score_thresholds.items(), 
                                          key=lambda x: x[1], reverse=True):
            if composite_score >= threshold:
                return trend_type
        
        return 'niche'
    
    def identify_rising_trends(self, trends: List[TrendKeyword], 
                             min_growth_rate: float = 5.0,
                             hours_window: int = 48) -> List[TrendKeyword]:
        """Identify trends that are currently rising"""
        cutoff_time = datetime.now() - timedelta(hours=hours_window)
        
        rising_trends = []
        for trend in trends:
            if (trend.last_updated >= cutoff_time and 
                trend.is_rising and 
                trend.score.growth_rate >= min_growth_rate):
                rising_trends.append(trend)
        
        # Sort by growth rate descending
        rising_trends.sort(key=lambda x: x.score.growth_rate, reverse=True)
        
        return rising_trends
    
    def predict_trend_trajectory(self, trend: TrendKeyword) -> Dict:
        """Predict where a trend is heading"""
        current_score = trend.score.current_score
        growth_rate = trend.score.growth_rate
        peak_score = trend.score.peak_score
        
        # Simple trajectory prediction
        prediction = {
            'current_phase': self._determine_trend_phase(trend),
            'predicted_direction': 'rising' if growth_rate > 0 else 'declining',
            'confidence': self._calculate_prediction_confidence(trend),
            'estimated_peak_in_days': None,
            'sustainability_score': self._calculate_sustainability(trend)
        }
        
        # Estimate peak timing if rising
        if growth_rate > 0:
            # Simple linear projection (very basic)
            days_to_peak = max(1, (100 - current_score) / max(growth_rate, 1) * 7)
            prediction['estimated_peak_in_days'] = min(days_to_peak, 30)  # Cap at 30 days
        
        return prediction
    
    def compare_trends(self, trend1: TrendKeyword, trend2: TrendKeyword) -> Dict:
        """Compare two trends across multiple dimensions"""
        score1 = self.calculate_composite_score(trend1)
        score2 = self.calculate_composite_score(trend2)
        
        comparison = {
            'trend1': {
                'keyword': trend1.keyword,
                'composite_score': score1,
                'category': trend1.category.value,
                'type': self.classify_trend_type(trend1)
            },
            'trend2': {
                'keyword': trend2.keyword,
                'composite_score': score2,
                'category': trend2.category.value,
                'type': self.classify_trend_type(trend2)
            },
            'winner': trend1.keyword if score1 > score2 else trend2.keyword,
            'score_difference': abs(score1 - score2),
            'advantages': self._identify_advantages(trend1, trend2)
        }
        
        return comparison
    
    def generate_trend_report(self, trends: List[TrendKeyword], 
                            time_period: str = "last_7_days") -> TrendReport:
        """Generate a comprehensive trend report"""
        analysis = self.analyze_trends(trends)
        
        # Sort trends by composite score
        scored_trends = [(trend, self.calculate_composite_score(trend)) for trend in trends]
        scored_trends.sort(key=lambda x: x[1], reverse=True)
        
        top_trends = [trend for trend, score in scored_trends[:10]]
        rising_trends = self.identify_rising_trends(trends)[:10]
        declining_trends = [t for t in trends if not t.is_rising and t.score.growth_rate < -2][:10]
        
        # Category breakdown
        category_breakdown = defaultdict(int)
        for trend in trends:
            category_breakdown[trend.category] += 1
        
        # Platform performance
        platform_performance = self._calculate_platform_averages(trends)
        
        report = TrendReport(
            report_id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            generated_at=datetime.now(),
            time_period=time_period,
            top_keywords=top_trends,
            rising_trends=rising_trends,
            declining_trends=declining_trends,
            category_breakdown=dict(category_breakdown),
            platform_performance=platform_performance,
            key_insights=analysis.get('insights', []),
            recommended_keywords=[t.keyword for t in rising_trends[:5]],
            content_opportunities=self._generate_content_opportunities(rising_trends, top_trends)
        )
        
        return report
    
    def _analyze_score_distribution(self, trends: List[TrendKeyword]) -> Dict:
        """Analyze the distribution of trend scores"""
        scores = [trend.score.current_score for trend in trends]
        
        return {
            'mean': statistics.mean(scores),
            'median': statistics.median(scores),
            'std_dev': statistics.stdev(scores) if len(scores) > 1 else 0,
            'min': min(scores),
            'max': max(scores),
            'quartiles': {
                'q1': statistics.quantiles(scores, n=4)[0] if len(scores) > 1 else 0,
                'q3': statistics.quantiles(scores, n=4)[2] if len(scores) > 1 else 0
            }
        }
    
    def _analyze_category_performance(self, trends: List[TrendKeyword]) -> Dict:
        """Analyze performance by category"""
        category_stats = defaultdict(list)
        
        for trend in trends:
            category_stats[trend.category].append({
                'score': trend.score.current_score,
                'growth_rate': trend.score.growth_rate
            })
        
        category_performance = {}
        for category, stats in category_stats.items():
            scores = [s['score'] for s in stats]
            growth_rates = [s['growth_rate'] for s in stats]
            
            category_performance[category.value] = {
                'count': len(stats),
                'avg_score': statistics.mean(scores),
                'avg_growth_rate': statistics.mean(growth_rates),
                'top_score': max(scores),
                'trending_count': len([g for g in growth_rates if g > 0])
            }
        
        return category_performance
    
    def _analyze_growth_patterns(self, trends: List[TrendKeyword]) -> Dict:
        """Analyze growth rate patterns"""
        growth_rates = [trend.score.growth_rate for trend in trends]
        
        return {
            'rising_trends': len([g for g in growth_rates if g > 0]),
            'declining_trends': len([g for g in growth_rates if g < 0]),
            'stable_trends': len([g for g in growth_rates if g == 0]),
            'avg_growth_rate': statistics.mean(growth_rates),
            'fastest_growing': max(growth_rates) if growth_rates else 0,
            'fastest_declining': min(growth_rates) if growth_rates else 0
        }
    
    def _analyze_platform_performance(self, trends: List[TrendKeyword]) -> Dict:
        """Analyze performance across platforms"""
        platform_data = defaultdict(list)
        
        for trend in trends:
            for metric in trend.platform_metrics:
                platform_data[metric.source].append(metric.engagement_score)
        
        platform_performance = {}
        for platform, scores in platform_data.items():
            platform_performance[platform.value] = {
                'trend_count': len(scores),
                'avg_engagement': statistics.mean(scores),
                'max_engagement': max(scores),
                'performance_rating': 'high' if statistics.mean(scores) > 70 else 
                                    'medium' if statistics.mean(scores) > 40 else 'low'
            }
        
        return platform_performance
    
    def _analyze_temporal_patterns(self, trends: List[TrendKeyword]) -> Dict:
        """Analyze temporal patterns in trend data"""
        now = datetime.now()
        
        # Group by time periods
        time_buckets = {
            'last_24h': 0,
            'last_week': 0,
            'last_month': 0,
            'older': 0
        }
        
        for trend in trends:
            hours_ago = (now - trend.last_updated).total_seconds() / 3600
            
            if hours_ago <= 24:
                time_buckets['last_24h'] += 1
            elif hours_ago <= 168:  # 1 week
                time_buckets['last_week'] += 1
            elif hours_ago <= 720:  # 1 month
                time_buckets['last_month'] += 1
            else:
                time_buckets['older'] += 1
        
        return time_buckets
    
    def _get_top_performers(self, trends: List[TrendKeyword], limit: int = 10) -> List[Dict]:
        """Get top performing trends with scores"""
        scored_trends = []
        
        for trend in trends:
            composite_score = self.calculate_composite_score(trend)
            trend_type = self.classify_trend_type(trend)
            
            scored_trends.append({
                'keyword': trend.keyword,
                'category': trend.category.value,
                'current_score': trend.score.current_score,
                'composite_score': composite_score,
                'growth_rate': trend.score.growth_rate,
                'type': trend_type,
                'is_rising': trend.is_rising
            })
        
        # Sort by composite score
        scored_trends.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return scored_trends[:limit]
    
    def _generate_recommendations(self, trends: List[TrendKeyword]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        rising_trends = self.identify_rising_trends(trends)
        
        if rising_trends:
            top_rising = rising_trends[0]
            recommendations.append(
                f"Focus on '{top_rising.keyword}' - fastest growing trend with "
                f"{top_rising.score.growth_rate:.1f}% growth rate"
            )
        
        # Category recommendations
        category_stats = self._analyze_category_performance(trends)
        if category_stats:
            top_category = max(category_stats.items(), 
                             key=lambda x: x[1]['avg_score'])
            recommendations.append(
                f"Prioritize {top_category[0].replace('_', ' ')} content - "
                f"highest performing category with {top_category[1]['avg_score']:.1f} avg score"
            )
        
        # Platform recommendations
        platform_stats = self._analyze_platform_performance(trends)
        if platform_stats:
            top_platform = max(platform_stats.items(),
                             key=lambda x: x[1]['avg_engagement'])
            recommendations.append(
                f"Leverage {top_platform[0].replace('_', ' ')} - "
                f"best performing platform with {top_platform[1]['avg_engagement']:.1f} avg engagement"
            )
        
        return recommendations
    
    def _generate_insights(self, trends: List[TrendKeyword]) -> List[str]:
        """Generate data-driven insights"""
        insights = []
        
        growth_analysis = self._analyze_growth_patterns(trends)
        score_distribution = self._analyze_score_distribution(trends)
        
        # Growth insights
        rising_pct = (growth_analysis['rising_trends'] / len(trends)) * 100
        insights.append(f"{rising_pct:.1f}% of trends are currently rising")
        
        # Score insights
        if score_distribution['mean'] > 60:
            insights.append("Strong overall trend performance - high engagement potential")
        elif score_distribution['mean'] > 30:
            insights.append("Moderate trend performance - selective content opportunities")
        else:
            insights.append("Lower trend scores - focus on emerging opportunities")
        
        # Volatility insight
        if score_distribution['std_dev'] > 25:
            insights.append("High trend volatility - both high-potential and risky opportunities")
        else:
            insights.append("Stable trend landscape - consistent content performance expected")
        
        return insights
    
    def _determine_trend_phase(self, trend: TrendKeyword) -> str:
        """Determine what phase a trend is in"""
        current = trend.score.current_score
        peak = trend.score.peak_score
        growth = trend.score.growth_rate
        
        if current < peak * 0.3:
            return 'early' if growth > 0 else 'declining'
        elif current < peak * 0.7:
            return 'growing' if growth > 0 else 'plateau'
        else:
            return 'peak' if abs(growth) < 2 else 'mature'
    
    def _calculate_prediction_confidence(self, trend: TrendKeyword) -> float:
        """Calculate confidence in trend prediction"""
        # Base confidence on data recency and consistency
        hours_old = (datetime.now() - trend.last_updated).total_seconds() / 3600
        recency_factor = max(0, 1.0 - hours_old / 24)  # Confidence decreases with age
        
        # Consistency factor (how stable the trend has been)
        if trend.score.peak_score > 0:
            consistency = trend.score.current_score / trend.score.peak_score
        else:
            consistency = 0.5
        
        confidence = (recency_factor * 0.6) + (consistency * 0.4)
        return confidence
    
    def _calculate_sustainability(self, trend: TrendKeyword) -> float:
        """Calculate how sustainable a trend is likely to be"""
        # Factors that contribute to sustainability
        factors = []
        
        # Platform diversity (more platforms = more sustainable)
        platform_diversity = len(trend.platform_metrics) / 5.0  # Normalize to max 5
        factors.append(platform_diversity)
        
        # Growth stability (moderate growth more sustainable than explosive)
        growth_stability = 1.0 - abs(trend.score.growth_rate) / 100.0
        factors.append(max(0, growth_stability))
        
        # Score consistency
        if trend.score.peak_score > 0:
            consistency = trend.score.current_score / trend.score.peak_score
        else:
            consistency = 0.5
        factors.append(consistency)
        
        return statistics.mean(factors)
    
    def _identify_advantages(self, trend1: TrendKeyword, trend2: TrendKeyword) -> Dict:
        """Identify advantages of one trend over another"""
        advantages = {'trend1': [], 'trend2': []}
        
        # Score comparison
        if trend1.score.current_score > trend2.score.current_score:
            advantages['trend1'].append('Higher current score')
        else:
            advantages['trend2'].append('Higher current score')
        
        # Growth rate comparison
        if trend1.score.growth_rate > trend2.score.growth_rate:
            advantages['trend1'].append('Faster growth rate')
        else:
            advantages['trend2'].append('Faster growth rate')
        
        # Platform presence
        if len(trend1.platform_metrics) > len(trend2.platform_metrics):
            advantages['trend1'].append('More platform coverage')
        else:
            advantages['trend2'].append('More platform coverage')
        
        return advantages
    
    def _calculate_platform_averages(self, trends: List[TrendKeyword]) -> Dict[TrendSource, float]:
        """Calculate average scores per platform"""
        platform_scores = defaultdict(list)
        
        for trend in trends:
            for metric in trend.platform_metrics:
                platform_scores[metric.source].append(metric.engagement_score)
        
        return {
            platform: statistics.mean(scores)
            for platform, scores in platform_scores.items()
        }
    
    def _generate_content_opportunities(self, rising_trends: List[TrendKeyword],
                                      top_trends: List[TrendKeyword]) -> List[str]:
        """Generate specific content opportunities"""
        opportunities = []
        
        # From rising trends
        for trend in rising_trends[:3]:
            opportunities.append(
                f"Create timely content around '{trend.keyword}' - rising {trend.score.growth_rate:.1f}% "
                f"in {trend.category.value.replace('_', ' ')} category"
            )
        
        # From top performers
        for trend in top_trends[:2]:
            if trend.score.current_score > 70:
                opportunities.append(
                    f"Leverage established trend '{trend.keyword}' - "
                    f"high engagement potential ({trend.score.current_score:.1f} score)"
                )
        
        return opportunities