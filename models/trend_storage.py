from typing import List, Dict, Optional
from datetime import datetime, timedelta
import sqlite3
import json
from pathlib import Path

from models.trend import TrendKeyword, TrendReport, AccountTrendProfile, TrendCategory, TrendSource


class TrendStorage:
    """SQLite-based storage for trend data with JSON fallback"""
    
    def __init__(self, db_path: str = "data/trends/trends.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Trend keywords table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_keywords (
                keyword TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                current_score REAL NOT NULL,
                peak_score REAL NOT NULL,
                growth_rate REAL NOT NULL,
                search_volume INTEGER,
                competition_level TEXT,
                related_keywords TEXT, -- JSON array
                regional_data TEXT,    -- JSON array
                platform_metrics TEXT, -- JSON array
                seasonality TEXT,      -- JSON object
                first_detected TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                is_rising BOOLEAN NOT NULL,
                estimated_peak TEXT
            )
        ''')
        
        # Trend reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_reports (
                report_id TEXT PRIMARY KEY,
                generated_at TEXT NOT NULL,
                time_period TEXT NOT NULL,
                top_keywords TEXT,      -- JSON array
                rising_trends TEXT,     -- JSON array
                declining_trends TEXT,  -- JSON array
                category_breakdown TEXT, -- JSON object
                platform_performance TEXT, -- JSON object
                key_insights TEXT,      -- JSON array
                recommended_keywords TEXT, -- JSON array
                content_opportunities TEXT -- JSON array
            )
        ''')
        
        # Account trend profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_trend_profiles (
                account_id TEXT PRIMARY KEY,
                preferred_categories TEXT, -- JSON array
                excluded_keywords TEXT,    -- JSON array
                target_regions TEXT,       -- JSON array
                min_trend_score REAL NOT NULL,
                successful_trends TEXT,    -- JSON array
                trend_adoption_rate REAL,
                preferred_platforms TEXT,  -- JSON array
                watching_keywords TEXT,    -- JSON array
                last_trend_update TEXT
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords_category ON trend_keywords(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords_score ON trend_keywords(current_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords_updated ON trend_keywords(last_updated)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_generated ON trend_reports(generated_at)')
        
        conn.commit()
        conn.close()
    
    def save_trend_keyword(self, trend: TrendKeyword):
        """Save a trend keyword to the database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO trend_keywords (
                keyword, category, current_score, peak_score, growth_rate,
                search_volume, competition_level, related_keywords, regional_data,
                platform_metrics, seasonality, first_detected, last_updated,
                is_rising, estimated_peak
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trend.keyword,
            trend.category.value,
            trend.score.current_score,
            trend.score.peak_score,
            trend.score.growth_rate,
            trend.search_volume,
            trend.competition_level,
            json.dumps(trend.related_keywords),
            json.dumps([rd.model_dump(mode='json') for rd in trend.regional_data]),
            json.dumps([pm.model_dump(mode='json') for pm in trend.platform_metrics]),
            json.dumps(trend.seasonality),
            trend.first_detected.isoformat(),
            trend.last_updated.isoformat(),
            trend.is_rising,
            trend.estimated_peak.isoformat() if trend.estimated_peak else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_trend_keyword(self, keyword: str) -> Optional[TrendKeyword]:
        """Retrieve a specific trend keyword"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM trend_keywords WHERE keyword = ?', (keyword,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_trend_keyword(row)
    
    def get_trending_keywords(self, category: Optional[TrendCategory] = None,
                            min_score: float = 0.0,
                            limit: int = 20) -> List[TrendKeyword]:
        """Get trending keywords with filters"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = 'SELECT * FROM trend_keywords WHERE current_score >= ?'
        params = [min_score]
        
        if category:
            query += ' AND category = ?'
            params.append(category.value)
        
        query += ' ORDER BY current_score DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_trend_keyword(row) for row in rows]
    
    def get_rising_trends(self, hours: int = 24, limit: int = 10) -> List[TrendKeyword]:
        """Get rising trends from the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trend_keywords 
            WHERE last_updated >= ? AND is_rising = 1 AND growth_rate > 0
            ORDER BY growth_rate DESC LIMIT ?
        ''', (cutoff.isoformat(), limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_trend_keyword(row) for row in rows]
    
    def save_trend_report(self, report: TrendReport):
        """Save a trend report to the database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO trend_reports (
                report_id, generated_at, time_period, top_keywords, rising_trends,
                declining_trends, category_breakdown, platform_performance,
                key_insights, recommended_keywords, content_opportunities
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report.report_id,
            report.generated_at.isoformat(),
            report.time_period,
            json.dumps([kw.model_dump(mode='json') for kw in report.top_keywords]),
            json.dumps([kw.model_dump(mode='json') for kw in report.rising_trends]),
            json.dumps([kw.model_dump(mode='json') for kw in report.declining_trends]),
            json.dumps({k.value: v for k, v in report.category_breakdown.items()}),
            json.dumps({k.value: v for k, v in report.platform_performance.items()}),
            json.dumps(report.key_insights),
            json.dumps(report.recommended_keywords),
            json.dumps(report.content_opportunities)
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_reports(self, limit: int = 10) -> List[TrendReport]:
        """Get recent trend reports"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trend_reports 
            ORDER BY generated_at DESC LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_trend_report(row) for row in rows]
    
    def save_account_profile(self, profile: AccountTrendProfile):
        """Save account trend profile"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO account_trend_profiles (
                account_id, preferred_categories, excluded_keywords, target_regions,
                min_trend_score, successful_trends, trend_adoption_rate,
                preferred_platforms, watching_keywords, last_trend_update
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile.account_id,
            json.dumps([cat.value for cat in profile.preferred_categories]),
            json.dumps(profile.excluded_keywords),
            json.dumps(profile.target_regions),
            profile.min_trend_score,
            json.dumps(profile.successful_trends),
            profile.trend_adoption_rate,
            json.dumps([pf.value for pf in profile.preferred_platforms]),
            json.dumps(profile.watching_keywords),
            profile.last_trend_update.isoformat() if profile.last_trend_update else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_account_profile(self, account_id: str) -> Optional[AccountTrendProfile]:
        """Get account trend profile"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM account_trend_profiles WHERE account_id = ?', (account_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_account_profile(row)
    
    def _row_to_trend_keyword(self, row) -> TrendKeyword:
        """Convert database row to TrendKeyword object"""
        from models.trend import TrendScore, RegionalData, PlatformMetrics
        
        (keyword, category, current_score, peak_score, growth_rate, search_volume,
         competition_level, related_keywords_json, regional_data_json, 
         platform_metrics_json, seasonality_json, first_detected, last_updated,
         is_rising, estimated_peak) = row
        
        # Parse JSON fields
        related_keywords = json.loads(related_keywords_json) if related_keywords_json else []
        regional_data = [RegionalData(**rd) for rd in json.loads(regional_data_json)] if regional_data_json else []
        platform_metrics = [PlatformMetrics(**pm) for pm in json.loads(platform_metrics_json)] if platform_metrics_json else []
        seasonality = json.loads(seasonality_json) if seasonality_json else {}
        
        return TrendKeyword(
            keyword=keyword,
            category=TrendCategory(category),
            score=TrendScore(
                current_score=current_score,
                peak_score=peak_score,
                growth_rate=growth_rate
            ),
            regional_data=regional_data,
            platform_metrics=platform_metrics,
            related_keywords=related_keywords,
            search_volume=search_volume,
            competition_level=competition_level,
            seasonality=seasonality,
            first_detected=datetime.fromisoformat(first_detected),
            last_updated=datetime.fromisoformat(last_updated),
            is_rising=bool(is_rising),
            estimated_peak=datetime.fromisoformat(estimated_peak) if estimated_peak else None
        )
    
    def _row_to_trend_report(self, row) -> TrendReport:
        """Convert database row to TrendReport object"""
        # Implementation would parse the JSON fields back to TrendReport
        # This is a simplified version - full implementation would reconstruct all nested objects
        pass
    
    def _row_to_account_profile(self, row) -> AccountTrendProfile:
        """Convert database row to AccountTrendProfile object"""
        (account_id, preferred_categories_json, excluded_keywords_json, target_regions_json,
         min_trend_score, successful_trends_json, trend_adoption_rate, preferred_platforms_json,
         watching_keywords_json, last_trend_update) = row
        
        return AccountTrendProfile(
            account_id=account_id,
            preferred_categories=[TrendCategory(cat) for cat in json.loads(preferred_categories_json)] if preferred_categories_json else [],
            excluded_keywords=json.loads(excluded_keywords_json) if excluded_keywords_json else [],
            target_regions=json.loads(target_regions_json) if target_regions_json else [],
            min_trend_score=min_trend_score,
            successful_trends=json.loads(successful_trends_json) if successful_trends_json else [],
            trend_adoption_rate=trend_adoption_rate,
            preferred_platforms=[TrendSource(pf) for pf in json.loads(preferred_platforms_json)] if preferred_platforms_json else [],
            watching_keywords=json.loads(watching_keywords_json) if watching_keywords_json else [],
            last_trend_update=datetime.fromisoformat(last_trend_update) if last_trend_update else None
        )
    
    def cleanup_old_data(self, days: int = 30):
        """Remove old trend data"""
        cutoff = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Remove old keywords
        cursor.execute('DELETE FROM trend_keywords WHERE last_updated < ?', (cutoff.isoformat(),))
        
        # Remove old reports
        cursor.execute('DELETE FROM trend_reports WHERE generated_at < ?', (cutoff.isoformat(),))
        
        conn.commit()
        changes = conn.total_changes
        conn.close()
        
        return changes
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        stats = {}
        
        # Count keywords
        cursor.execute('SELECT COUNT(*) FROM trend_keywords')
        stats['total_keywords'] = cursor.fetchone()[0]
        
        # Count reports
        cursor.execute('SELECT COUNT(*) FROM trend_reports')
        stats['total_reports'] = cursor.fetchone()[0]
        
        # Count profiles
        cursor.execute('SELECT COUNT(*) FROM account_trend_profiles')
        stats['account_profiles'] = cursor.fetchone()[0]
        
        # Average score
        cursor.execute('SELECT AVG(current_score) FROM trend_keywords')
        result = cursor.fetchone()[0]
        stats['avg_score'] = result if result else 0
        
        # Categories
        cursor.execute('SELECT COUNT(DISTINCT category) FROM trend_keywords')
        stats['categories'] = cursor.fetchone()[0]
        
        conn.close()
        
        return stats