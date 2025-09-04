from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore

from services.trend_scraper import TrendScraper
from services.trend_analyzer import TrendAnalyzer
from models.trend import TrendCategory


class TrendScheduler:
    """Automated scheduler for trend scraping and analysis tasks"""
    
    def __init__(self, data_dir: str = "data/trends"):
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            timezone='UTC'
        )
        self.scraper = TrendScraper(data_dir)
        self.analyzer = TrendAnalyzer()
        
        # Track job status
        self.job_status = {}
        self.last_run_times = {}
        
        # Configuration for different scraping schedules
        self.scraping_schedules = {
            'hourly_quick': {
                'name': 'Hourly Quick Scrape',
                'description': 'Quick trending topics scrape every hour',
                'trigger': IntervalTrigger(hours=1),
                'job_func': self._hourly_quick_scrape,
                'enabled': True
            },
            'daily_full': {
                'name': 'Daily Full Scrape',
                'description': 'Comprehensive trend scraping daily',
                'trigger': CronTrigger(hour=6, minute=0),  # 6 AM UTC
                'job_func': self._daily_full_scrape,
                'enabled': True
            },
            'weekly_analysis': {
                'name': 'Weekly Analysis Report',
                'description': 'Generate weekly trend analysis report',
                'trigger': CronTrigger(day_of_week='mon', hour=8, minute=0),  # Monday 8 AM
                'job_func': self._weekly_analysis,
                'enabled': True
            },
            'daily_cleanup': {
                'name': 'Daily Data Cleanup',
                'description': 'Clean up old trend data daily',
                'trigger': CronTrigger(hour=2, minute=0),  # 2 AM UTC
                'job_func': self._daily_cleanup,
                'enabled': True
            }
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def start(self):
        """Start the trend scheduler"""
        try:
            # Add jobs to scheduler
            for job_id, config in self.scraping_schedules.items():
                if config['enabled']:
                    self.scheduler.add_job(
                        func=config['job_func'],
                        trigger=config['trigger'],
                        id=job_id,
                        name=config['name'],
                        replace_existing=True,
                        max_instances=1  # Prevent overlapping jobs
                    )
                    self.logger.info(f"Scheduled job: {config['name']}")
            
            self.scheduler.start()
            self.logger.info("Trend scheduler started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the trend scheduler"""
        try:
            self.scheduler.shutdown(wait=False)
            self.logger.info("Trend scheduler stopped")
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
    
    def get_job_status(self) -> Dict[str, Any]:
        """Get status of all scheduled jobs"""
        status = {}
        
        for job_id, config in self.scraping_schedules.items():
            job = self.scheduler.get_job(job_id)
            
            status[job_id] = {
                'name': config['name'],
                'description': config['description'],
                'enabled': config['enabled'],
                'next_run': job.next_run_time.isoformat() if job and job.next_run_time else None,
                'last_run': self.last_run_times.get(job_id),
                'status': self.job_status.get(job_id, 'Not run yet')
            }
        
        return status
    
    def pause_job(self, job_id: str):
        """Pause a specific job"""
        try:
            self.scheduler.pause_job(job_id)
            self.logger.info(f"Paused job: {job_id}")
        except Exception as e:
            self.logger.error(f"Failed to pause job {job_id}: {e}")
    
    def resume_job(self, job_id: str):
        """Resume a paused job"""
        try:
            self.scheduler.resume_job(job_id)
            self.logger.info(f"Resumed job: {job_id}")
        except Exception as e:
            self.logger.error(f"Failed to resume job {job_id}: {e}")
    
    def run_job_now(self, job_id: str):
        """Trigger a job to run immediately"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.modify(next_run_time=datetime.now())
                self.logger.info(f"Triggered job: {job_id}")
            else:
                self.logger.error(f"Job not found: {job_id}")
        except Exception as e:
            self.logger.error(f"Failed to trigger job {job_id}: {e}")
    
    async def _hourly_quick_scrape(self):
        """Hourly quick scrape of trending topics"""
        job_id = 'hourly_quick'
        self.logger.info("Starting hourly quick scrape...")
        
        try:
            self.job_status[job_id] = 'Running'
            self.last_run_times[job_id] = datetime.now().isoformat()
            
            # Quick scrape of trending topics
            trends = self.scraper.scrape_trending_topics_only(limit=20)
            
            self.job_status[job_id] = f'Completed - {len(trends)} trends found'
            self.logger.info(f"Hourly quick scrape completed: {len(trends)} trends")
            
        except Exception as e:
            self.job_status[job_id] = f'Failed: {str(e)}'
            self.logger.error(f"Hourly quick scrape failed: {e}")
    
    async def _daily_full_scrape(self):
        """Daily comprehensive trend scraping"""
        job_id = 'daily_full'
        self.logger.info("Starting daily full scrape...")
        
        try:
            self.job_status[job_id] = 'Running'
            self.last_run_times[job_id] = datetime.now().isoformat()
            
            # Full comprehensive scrape
            all_trends = self.scraper.scrape_all_trends(
                geo='US',
                timeframe='today 1-d',
                max_keywords=100
            )
            
            total_trends = sum(len(trends) for trends in all_trends.values())
            self.job_status[job_id] = f'Completed - {total_trends} total trends collected'
            self.logger.info(f"Daily full scrape completed: {total_trends} trends")
            
            # Generate daily insights
            await self._generate_daily_insights()
            
        except Exception as e:
            self.job_status[job_id] = f'Failed: {str(e)}'
            self.logger.error(f"Daily full scrape failed: {e}")
    
    async def _weekly_analysis(self):
        """Weekly trend analysis and reporting"""
        job_id = 'weekly_analysis'
        self.logger.info("Starting weekly analysis...")
        
        try:
            self.job_status[job_id] = 'Running'
            self.last_run_times[job_id] = datetime.now().isoformat()
            
            # Get trends for analysis
            trends = self.scraper.trend_storage.get_trending_keywords(limit=200)
            
            if trends:
                # Generate comprehensive analysis
                analysis = self.analyzer.analyze_trends(trends)
                
                # Generate weekly report
                report = self.analyzer.generate_trend_report(trends, 'last_7_days')
                
                # Save report to file
                report_file = f"data/trends/weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
                self._save_analysis_report(analysis, report, report_file)
                
                self.job_status[job_id] = f'Completed - Report saved to {report_file}'
                self.logger.info(f"Weekly analysis completed: {len(trends)} trends analyzed")
            else:
                self.job_status[job_id] = 'Completed - No trends available for analysis'
                self.logger.warning("Weekly analysis: No trends available")
                
        except Exception as e:
            self.job_status[job_id] = f'Failed: {str(e)}'
            self.logger.error(f"Weekly analysis failed: {e}")
    
    async def _daily_cleanup(self):
        """Daily cleanup of old trend data"""
        job_id = 'daily_cleanup'
        self.logger.info("Starting daily cleanup...")
        
        try:
            self.job_status[job_id] = 'Running'
            self.last_run_times[job_id] = datetime.now().isoformat()
            
            # Clean up trends older than 30 days
            removed_count = self.scraper.cleanup_old_trends(days=30)
            
            self.job_status[job_id] = f'Completed - Removed {removed_count} old records'
            self.logger.info(f"Daily cleanup completed: {removed_count} records removed")
            
        except Exception as e:
            self.job_status[job_id] = f'Failed: {str(e)}'
            self.logger.error(f"Daily cleanup failed: {e}")
    
    async def _generate_daily_insights(self):
        """Generate daily insights from fresh trend data"""
        try:
            # Get recent trends (last 24 hours)
            recent_trends = self.scraper.trend_storage.get_rising_trends(hours=24, limit=50)
            
            if recent_trends:
                # Analyze for quick insights
                insights = []
                
                # Top rising trend
                if recent_trends:
                    top_rising = max(recent_trends, key=lambda x: x.score.growth_rate)
                    insights.append(f"Fastest rising trend: {top_rising.keyword} (+{top_rising.score.growth_rate:.1f}%)")
                
                # Category distribution
                categories = {}
                for trend in recent_trends:
                    categories[trend.category] = categories.get(trend.category, 0) + 1
                
                if categories:
                    top_category = max(categories.keys(), key=lambda x: categories[x])
                    insights.append(f"Most active category: {top_category.value} ({categories[top_category]} trends)")
                
                # Log insights
                for insight in insights:
                    self.logger.info(f"Daily insight: {insight}")
                    
        except Exception as e:
            self.logger.error(f"Failed to generate daily insights: {e}")
    
    def _save_analysis_report(self, analysis: Dict, report: Any, filename: str):
        """Save analysis and report data to file"""
        try:
            from pathlib import Path
            import json
            
            # Ensure directory exists
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            
            # Combine analysis and report data
            combined_data = {
                'generated_at': datetime.now().isoformat(),
                'analysis': analysis,
                'report': {
                    'report_id': report.report_id,
                    'time_period': report.time_period,
                    'top_keywords': [{'keyword': t.keyword, 'score': t.score.current_score} 
                                   for t in report.top_keywords[:20]],
                    'rising_trends': [{'keyword': t.keyword, 'growth_rate': t.score.growth_rate} 
                                    for t in report.rising_trends[:20]],
                    'category_breakdown': {str(k): v for k, v in report.category_breakdown.items()},
                    'insights': report.key_insights,
                    'opportunities': report.content_opportunities,
                    'recommended_keywords': report.recommended_keywords
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(combined_data, f, indent=2, default=str)
                
            self.logger.info(f"Analysis report saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save analysis report: {e}")
    
    def add_custom_schedule(self, job_id: str, name: str, job_func: Callable, 
                          cron_expression: str = None, interval_hours: int = None):
        """Add a custom scheduled job"""
        try:
            # Create trigger based on parameters
            if cron_expression:
                # Parse cron expression (simplified)
                parts = cron_expression.split()
                if len(parts) >= 2:
                    minute, hour = parts[:2]
                    trigger = CronTrigger(minute=minute, hour=hour)
                else:
                    raise ValueError("Invalid cron expression")
            elif interval_hours:
                trigger = IntervalTrigger(hours=interval_hours)
            else:
                raise ValueError("Must specify either cron_expression or interval_hours")
            
            # Add job to scheduler
            self.scheduler.add_job(
                func=job_func,
                trigger=trigger,
                id=job_id,
                name=name,
                replace_existing=True,
                max_instances=1
            )
            
            self.logger.info(f"Added custom job: {name}")
            
        except Exception as e:
            self.logger.error(f"Failed to add custom job {job_id}: {e}")
    
    async def run_scheduler_loop(self):
        """Run the scheduler in an async loop (for standalone execution)"""
        try:
            self.start()
            
            # Keep the scheduler running
            while True:
                await asyncio.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        except Exception as e:
            self.logger.error(f"Scheduler loop error: {e}")
        finally:
            self.stop()


# Standalone execution function
async def main():
    """Main function for running the trend scheduler standalone"""
    scheduler = TrendScheduler()
    await scheduler.run_scheduler_loop()


if __name__ == "__main__":
    asyncio.run(main())