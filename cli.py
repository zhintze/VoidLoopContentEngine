import typer
import toml
from pathlib import Path
from datetime import datetime
from models.account import Account
from factories.output_factory import OutputFactory
from dotenv import load_dotenv
from services.instagram_api import InstagramAPIConfig
from services.pinterest_api import PinterestAPIConfig
from services.facebook_api import FacebookAPIConfig
from services.twitter_api import TwitterAPIConfig
from services.trend_scraper import TrendScraper
from services.trend_analyzer import TrendAnalyzer
from services.trend_filter import RecipeTrendFilter
from services.trend_scheduler import TrendScheduler
from models.trend import TrendCategory
import os
import json
import asyncio
import signal
import sys
load_dotenv()



app = typer.Typer()

ACCOUNTS_DIR = Path("accounts")
SCHEDULE_FILE = Path("scheduler/schedule.toml")
OUTPUT_DIR = Path("output")

@app.command()
def new_account(
        name: str,
        site: str,
        template_id: str = "recipe",
        instagram: str = "",
        pinterest: str = "",
        keywords: str = "",
        tone: str = "neutral",
        hashtags: str = ""
):
    """Create a new account TOML config."""
    account_path = ACCOUNTS_DIR / f"{name}.toml"
    data = {
        "account_id": name,
        "name": name,
        "template_id": template_id,
        "site": site,
        "social_handles": {
            "instagram": instagram,
            "pinterest": pinterest,
        },
        "keywords": [kw.strip() for kw in keywords.split(",") if kw.strip()],
        "tone": tone,
        "hashtags": [ht.strip() for ht in hashtags.split(",") if ht.strip()],
        "api_credentials": {
            "instagram_access_token": None,
            "instagram_page_id": None,
            "pinterest_access_token": None,
            "pinterest_board_name": "Recipes",
            "facebook_access_token": None,
            "facebook_page_id": None,
            "twitter_bearer_token": None,
            "twitter_api_key": None,
            "twitter_api_secret": None,
            "twitter_access_token": None,
            "twitter_access_token_secret": None,
            "default_image_url": None
        },
        "outputs": [],
        "post_queue": [],
        "log_entries": [],
    }
    ACCOUNTS_DIR.mkdir(exist_ok=True)
    with open(account_path, "w") as f:
        toml.dump(data, f)
    typer.echo(f"Created account: {account_path}")
    typer.echo("💡 Use 'set-credentials' command to add API keys for posting")

@app.command()
def schedule_post(account: str, template: str, day: str, time: str):
    """Add a scheduled post to the schedule TOML."""
    SCHEDULE_FILE.parent.mkdir(exist_ok=True)
    schedule = {"posts": []}
    if SCHEDULE_FILE.exists():
        schedule = toml.load(SCHEDULE_FILE)
    schedule.setdefault("posts", []).append({
        "account": account,
        "template": template,
        "day": day,
        "time": time
    })
    with open(SCHEDULE_FILE, "w") as f:
        toml.dump(schedule, f)
    typer.echo(f"Scheduled post for {account} on {day} at {time}")

@app.command()
def run_account(
        account_name: str,
        platform: str = typer.Option("blog", help="Platform to generate for: blog, instagram, pinterest, facebook, twitter"),
        offline: bool = typer.Option(False, "--offline", help="Run without calling the OpenAI API"),
        auto_post: bool = typer.Option(False, "--auto-post", help="Automatically post to the platform"),
        use_trends: bool = typer.Option(True, "--trends/--no-trends", help="Use trending topics to enhance content")
):
    """Run the full content generation flow for a given account."""
    account_path = ACCOUNTS_DIR / f"{account_name}.toml"
    if not account_path.exists():
        typer.echo(f"Account file not found: {account_path}")
        raise typer.Exit(code=1)

    try:
        account = Account.from_toml(str(account_path))
        typer.echo(f"Loaded account: {account.name}")
    except Exception as e:
        typer.echo(f"Failed to load account: {e}")
        raise typer.Exit(code=1)

    try:
        action = "Generating and posting" if auto_post else "Generating"
        trend_status = "with trending topics" if use_trends and not offline else "without trends"
        typer.echo(f"{action} {platform} content for account: {account.name} ({trend_status})")
        
        factory = OutputFactory(account, offline=offline, platform=platform, 
                              auto_post=auto_post, use_trends=use_trends)
        factory.run()
    except Exception as e:
        typer.echo(f"Error during content generation: {e}")
        raise typer.Exit(code=1)

@app.command()
def set_credentials(
    account_name: str,
    platform: str = typer.Option(None, help="Platform: instagram, pinterest, facebook, or twitter"),
    instagram_token: str = typer.Option(None, "--instagram-token", help="Instagram access token"),
    instagram_page_id: str = typer.Option(None, "--instagram-page-id", help="Instagram page ID"),
    pinterest_token: str = typer.Option(None, "--pinterest-token", help="Pinterest access token"),
    pinterest_board: str = typer.Option(None, "--pinterest-board", help="Pinterest board name"),
    facebook_token: str = typer.Option(None, "--facebook-token", help="Facebook page access token"),
    facebook_page_id: str = typer.Option(None, "--facebook-page-id", help="Facebook page ID"),
    twitter_bearer: str = typer.Option(None, "--twitter-bearer", help="Twitter Bearer token"),
    twitter_api_key: str = typer.Option(None, "--twitter-api-key", help="Twitter API key"),
    twitter_api_secret: str = typer.Option(None, "--twitter-api-secret", help="Twitter API secret"),
    twitter_access_token: str = typer.Option(None, "--twitter-access-token", help="Twitter access token"),
    twitter_access_secret: str = typer.Option(None, "--twitter-access-secret", help="Twitter access token secret"),
    image_url: str = typer.Option(None, "--image-url", help="Default image URL")
):
    """Set API credentials for an account."""
    account_path = ACCOUNTS_DIR / f"{account_name}.toml"
    if not account_path.exists():
        typer.echo(f"❌ Account file not found: {account_path}")
        raise typer.Exit(code=1)

    try:
        account = Account.from_toml(str(account_path))
    except Exception as e:
        typer.echo(f"❌ Failed to load account: {e}")
        raise typer.Exit(code=1)

    # Update credentials based on provided options
    updated = False
    
    if instagram_token:
        account.api_credentials.instagram_access_token = instagram_token
        updated = True
        typer.echo("✅ Updated Instagram access token")
    
    if instagram_page_id:
        account.api_credentials.instagram_page_id = instagram_page_id
        updated = True
        typer.echo("✅ Updated Instagram page ID")
    
    if pinterest_token:
        account.api_credentials.pinterest_access_token = pinterest_token
        updated = True
        typer.echo("✅ Updated Pinterest access token")
    
    if pinterest_board:
        account.api_credentials.pinterest_board_name = pinterest_board
        updated = True
        typer.echo(f"✅ Updated Pinterest board name to: {pinterest_board}")
    
    if facebook_token:
        account.api_credentials.facebook_access_token = facebook_token
        updated = True
        typer.echo("✅ Updated Facebook access token")
    
    if facebook_page_id:
        account.api_credentials.facebook_page_id = facebook_page_id
        updated = True
        typer.echo("✅ Updated Facebook page ID")
    
    if twitter_bearer:
        account.api_credentials.twitter_bearer_token = twitter_bearer
        updated = True
        typer.echo("✅ Updated Twitter Bearer token")
    
    if twitter_api_key:
        account.api_credentials.twitter_api_key = twitter_api_key
        updated = True
        typer.echo("✅ Updated Twitter API key")
    
    if twitter_api_secret:
        account.api_credentials.twitter_api_secret = twitter_api_secret
        updated = True
        typer.echo("✅ Updated Twitter API secret")
    
    if twitter_access_token:
        account.api_credentials.twitter_access_token = twitter_access_token
        updated = True
        typer.echo("✅ Updated Twitter access token")
    
    if twitter_access_secret:
        account.api_credentials.twitter_access_token_secret = twitter_access_secret
        updated = True
        typer.echo("✅ Updated Twitter access token secret")
    
    if image_url:
        account.api_credentials.default_image_url = image_url
        updated = True
        typer.echo(f"✅ Updated default image URL")
    
    if not updated:
        typer.echo("❌ No credentials provided. Use --help to see available options.")
        return
    
    # Save updated account
    account.save_to_toml(str(account_path))
    typer.echo(f"💾 Saved credentials to {account_path}")

@app.command()
def list_accounts():
    """List all accounts and their credential status."""
    if not ACCOUNTS_DIR.exists():
        typer.echo("No accounts directory found.")
        return
    
    account_files = list(ACCOUNTS_DIR.glob("*.toml"))
    if not account_files:
        typer.echo("No accounts found.")
        return
    
    typer.echo("=== Account Status ===\n")
    
    for account_file in account_files:
        try:
            account = Account.from_toml(str(account_file))
            typer.echo(f"📁 {account.name} ({account.account_id})")
            typer.echo(f"   Site: {account.site}")
            typer.echo(f"   Template: {account.template_id}")
            typer.echo(f"   Status: {account.status.value}")
            
            # API status
            status = account.get_platform_status()
            ig_status = "✅" if status['instagram'] else "❌"
            pin_status = "✅" if status['pinterest'] else "❌"
            fb_status = "✅" if status['facebook'] else "❌"
            tw_status = "✅" if status['twitter'] else "❌"
            typer.echo(f"   APIs: Instagram {ig_status} | Pinterest {pin_status} | Facebook {fb_status} | Twitter {tw_status}")
            
            if account.api_credentials.default_image_url:
                typer.echo(f"   Image: ✅ {account.api_credentials.default_image_url[:50]}...")
            else:
                typer.echo(f"   Image: ❌ No default image URL")
            
            typer.echo()
            
        except Exception as e:
            typer.echo(f"❌ Error loading {account_file.name}: {e}\n")

@app.command()
def test_api(
    account_name: str = typer.Option(None, help="Test specific account credentials"),
    platform: str = typer.Option(None, help="Platform to test: instagram, pinterest, facebook, or twitter")
):
    """Test API connectivity and authentication."""
    if not platform:
        typer.echo("❌ Please specify --platform instagram, pinterest, facebook, or twitter")
        return
    
    # Load account if specified
    account = None
    if account_name:
        account_path = ACCOUNTS_DIR / f"{account_name}.toml"
        if not account_path.exists():
            typer.echo(f"❌ Account file not found: {account_path}")
            return
        try:
            account = Account.from_toml(str(account_path))
            typer.echo(f"Testing {platform} API for account: {account.name}")
        except Exception as e:
            typer.echo(f"❌ Failed to load account: {e}")
            return
    
    if platform.lower() == "instagram":
        if account:
            api = InstagramAPIConfig.from_account(account)
            if not api:
                typer.echo("❌ No Instagram credentials configured for this account")
                typer.echo("💡 Use 'set-credentials' command to add them")
                return
        else:
            typer.echo("Testing Instagram API with environment variables...")
            api = InstagramAPIConfig.from_env()
            if not api:
                return
        
        info = api.get_account_info()
        if info:
            typer.echo(f"✅ Instagram API working! Account: {info.get('username', 'Unknown')}")
            typer.echo(f"   Followers: {info.get('followers_count', 'N/A')}")
        else:
            typer.echo("❌ Failed to get Instagram account info")
            
    elif platform.lower() == "pinterest":
        if account:
            api = PinterestAPIConfig.from_account(account)
            if not api:
                typer.echo("❌ No Pinterest credentials configured for this account")
                typer.echo("💡 Use 'set-credentials' command to add them")
                return
        else:
            typer.echo("Testing Pinterest API with environment variables...")
            api = PinterestAPIConfig.from_env()
            if not api:
                return
        
        info = api.get_user_info()
        if info:
            typer.echo(f"✅ Pinterest API working! Account: {info.get('username', 'Unknown')}")
            boards = api.get_boards()
            typer.echo(f"   Boards found: {len(boards)}")
            for board in boards[:3]:  # Show first 3 boards
                typer.echo(f"   - {board.get('name', 'Unnamed')}")
        else:
            typer.echo("❌ Failed to get Pinterest user info")
            
    elif platform.lower() == "facebook":
        if account:
            api = FacebookAPIConfig.from_account(account)
            if not api:
                typer.echo("❌ No Facebook credentials configured for this account")
                typer.echo("💡 Use 'set-credentials' command to add them")
                return
        else:
            typer.echo("Testing Facebook API with environment variables...")
            api = FacebookAPIConfig.from_env()
            if not api:
                return
        
        info = api.get_page_info()
        if info:
            typer.echo(f"✅ Facebook API working! Page: {info.get('name', 'Unknown')}")
            typer.echo(f"   Followers: {info.get('fan_count', 'N/A')}")
        else:
            typer.echo("❌ Failed to get Facebook page info")
            
    elif platform.lower() == "twitter":
        if account:
            api = TwitterAPIConfig.from_account(account)
            if not api:
                typer.echo("❌ No Twitter credentials configured for this account")
                typer.echo("💡 Use 'set-credentials' command to add them")
                return
        else:
            typer.echo("Testing Twitter API with environment variables...")
            api = TwitterAPIConfig.from_env()
            if not api:
                return
        
        info = api.get_user_info()
        if info:
            typer.echo(f"✅ Twitter API working! Account: @{info.get('username', 'Unknown')}")
            metrics = info.get('public_metrics', {})
            typer.echo(f"   Followers: {metrics.get('followers_count', 'N/A')}")
        else:
            typer.echo("❌ Failed to get Twitter user info")
    else:
        typer.echo("❌ Invalid platform. Use 'instagram', 'pinterest', 'facebook', or 'twitter'")

@app.command()
def setup_env():
    """Show environment variables needed for API integration."""
    typer.echo("=== Required Environment Variables ===\n")
    
    typer.echo("🔹 Instagram (Graph API):")
    typer.echo("   INSTAGRAM_ACCESS_TOKEN=your_long_lived_token")
    typer.echo("   INSTAGRAM_PAGE_ID=your_instagram_business_page_id")
    typer.echo("   DEFAULT_RECIPE_IMAGE_URL=https://your-image-host.com/default.jpg")
    typer.echo()
    
    typer.echo("🔹 Pinterest (API v5):")
    typer.echo("   PINTEREST_ACCESS_TOKEN=your_pinterest_token")
    typer.echo("   PINTEREST_BOARD_NAME=Recipes")
    typer.echo()
    
    typer.echo("🔹 Facebook (Pages API):")
    typer.echo("   FACEBOOK_ACCESS_TOKEN=your_page_access_token")
    typer.echo("   FACEBOOK_PAGE_ID=your_page_id")
    typer.echo()
    
    typer.echo("🔹 Twitter/X (API v2):")
    typer.echo("   TWITTER_BEARER_TOKEN=your_bearer_token")
    typer.echo("   TWITTER_API_KEY=your_api_key (optional)")
    typer.echo("   TWITTER_API_SECRET=your_api_secret (optional)")
    typer.echo("   TWITTER_ACCESS_TOKEN=your_access_token (optional)")
    typer.echo("   TWITTER_ACCESS_TOKEN_SECRET=your_access_secret (optional)")
    typer.echo()
    
    typer.echo("🔹 OpenAI:")
    typer.echo("   OPENAI_API_KEY=your_openai_api_key")
    typer.echo()
    
    typer.echo("💡 Add these to your .env file or export them as environment variables")

# ===== TREND MANAGEMENT COMMANDS =====

@app.command()
def scrape_trends(
    geo: str = typer.Option("US", help="Geographic location (US, GB, CA, etc.)"),
    timeframe: str = typer.Option("today 7-d", help="Time range (today 1-d, today 7-d, today 1-m)"),
    max_keywords: int = typer.Option(50, help="Maximum keywords to collect"),
    quick: bool = typer.Option(False, help="Quick scrape (trending topics only)")
):
    """Scrape food/recipe trends from Google Trends."""
    typer.echo("🔍 Starting trend scraping...")
    
    try:
        scraper = TrendScraper()
        
        if quick:
            trends = scraper.scrape_trending_topics_only(geo=geo, limit=max_keywords)
            typer.echo(f"📈 Found {len(trends)} trending topics:")
        else:
            all_trends = scraper.scrape_all_trends(geo=geo, timeframe=timeframe, max_keywords=max_keywords)
            total_trends = sum(len(trends) for trends in all_trends.values())
            typer.echo(f"📊 Comprehensive scrape complete! {total_trends} total trends found")
            
            for source, trends in all_trends.items():
                typer.echo(f"  📋 {source}: {len(trends)} trends")
            
            trends = []
            for trend_list in all_trends.values():
                trends.extend(trend_list)
        
        # Show top trends
        if trends:
            typer.echo("\n🔥 Top Trending Keywords:")
            for i, trend in enumerate(trends[:10], 1):
                growth_emoji = "📈" if trend.is_rising else "📉"
                typer.echo(f"  {i:2d}. {trend.keyword} ({trend.category.value}) "
                          f"- Score: {trend.score.current_score:.1f} {growth_emoji}")
        
        typer.echo(f"\n✅ Trends saved to database")
        
    except Exception as e:
        typer.echo(f"❌ Error scraping trends: {e}")

@app.command()
def list_trends(
    category: str = typer.Option(None, help="Filter by category"),
    limit: int = typer.Option(20, help="Number of trends to show"),
    min_score: float = typer.Option(0.0, help="Minimum trend score"),
    rising_only: bool = typer.Option(False, help="Show only rising trends")
):
    """List current trends in the database."""
    try:
        scraper = TrendScraper()
        
        if rising_only:
            trends = scraper.trend_storage.get_rising_trends(hours=48, limit=limit)
            typer.echo("📈 Rising Trends (Last 48 Hours):")
        else:
            # Convert category string to enum if provided
            category_filter = None
            if category:
                try:
                    category_filter = TrendCategory(category.lower())
                except ValueError:
                    typer.echo(f"❌ Invalid category: {category}")
                    typer.echo(f"Valid categories: {', '.join([c.value for c in TrendCategory])}")
                    return
            
            trends = scraper.trend_storage.get_trending_keywords(
                category=category_filter, 
                min_score=min_score, 
                limit=limit
            )
            title = f"📊 Current Trends"
            if category_filter:
                title += f" ({category_filter.value})"
            if min_score > 0:
                title += f" (Score ≥ {min_score})"
            typer.echo(title + ":")
        
        if not trends:
            typer.echo("No trends found matching your criteria.")
            return
        
        for i, trend in enumerate(trends, 1):
            growth_emoji = "📈" if trend.is_rising else "📉"
            growth_text = f"+{trend.score.growth_rate:.1f}%" if trend.score.growth_rate > 0 else f"{trend.score.growth_rate:.1f}%"
            
            typer.echo(f"{i:2d}. {trend.keyword}")
            typer.echo(f"    Category: {trend.category.value} | Score: {trend.score.current_score:.1f} | Growth: {growth_text} {growth_emoji}")
            typer.echo(f"    Updated: {trend.last_updated.strftime('%Y-%m-%d %H:%M')}")
            
            if trend.related_keywords:
                related = ', '.join(trend.related_keywords[:3])
                typer.echo(f"    Related: {related}")
            typer.echo()
            
    except Exception as e:
        typer.echo(f"❌ Error listing trends: {e}")

@app.command()
def analyze_trends(
    category: str = typer.Option(None, help="Analyze specific category"),
    days: int = typer.Option(7, help="Analysis period in days"),
    export: str = typer.Option(None, help="Export analysis to file (JSON)")
):
    """Analyze trend performance and generate insights."""
    try:
        scraper = TrendScraper()
        analyzer = TrendAnalyzer()
        
        # Get trends for analysis
        if category:
            try:
                category_filter = TrendCategory(category.lower())
                trends = scraper.trend_storage.get_trending_keywords(category=category_filter, limit=100)
                typer.echo(f"📊 Analyzing {category_filter.value} trends...")
            except ValueError:
                typer.echo(f"❌ Invalid category: {category}")
                return
        else:
            trends = scraper.trend_storage.get_trending_keywords(limit=100)
            typer.echo("📊 Analyzing all trends...")
        
        if not trends:
            typer.echo("No trends found for analysis.")
            return
        
        # Perform analysis
        analysis = analyzer.analyze_trends(trends)
        
        # Display key insights
        typer.echo(f"\n🔍 Analysis Results ({analysis['total_trends']} trends analyzed):")
        typer.echo(f"   Average Score: {analysis['score_distribution']['mean']:.1f}")
        typer.echo(f"   Score Range: {analysis['score_distribution']['min']:.1f} - {analysis['score_distribution']['max']:.1f}")
        
        # Growth analysis
        growth = analysis['growth_analysis']
        typer.echo(f"\n📈 Growth Patterns:")
        typer.echo(f"   Rising: {growth['rising_trends']} trends")
        typer.echo(f"   Declining: {growth['declining_trends']} trends")
        typer.echo(f"   Average Growth Rate: {growth['avg_growth_rate']:.1f}%")
        
        # Top performers
        typer.echo(f"\n🏆 Top Performers:")
        for i, performer in enumerate(analysis['top_performers'][:5], 1):
            typer.echo(f"   {i}. {performer['keyword']} - Score: {performer['current_score']:.1f} "
                      f"({performer['type']})")
        
        # Key insights
        if analysis['insights']:
            typer.echo(f"\n💡 Key Insights:")
            for insight in analysis['insights']:
                typer.echo(f"   • {insight}")
        
        # Recommendations
        if analysis['recommendations']:
            typer.echo(f"\n🎯 Recommendations:")
            for rec in analysis['recommendations']:
                typer.echo(f"   • {rec}")
        
        # Export if requested
        if export:
            export_path = Path(export)
            export_path.write_text(json.dumps(analysis, indent=2, default=str))
            typer.echo(f"\n💾 Analysis exported to {export_path}")
        
    except Exception as e:
        typer.echo(f"❌ Error analyzing trends: {e}")

@app.command()
def generate_report(
    time_period: str = typer.Option("last_7_days", help="Report time period"),
    output_file: str = typer.Option(None, help="Save report to file")
):
    """Generate a comprehensive trend report."""
    try:
        scraper = TrendScraper()
        analyzer = TrendAnalyzer()
        
        # Get trends for report
        trends = scraper.trend_storage.get_trending_keywords(limit=100)
        
        if not trends:
            typer.echo("No trends available for report generation.")
            return
        
        # Generate report
        typer.echo("📄 Generating comprehensive trend report...")
        report = analyzer.generate_trend_report(trends, time_period)
        
        # Display report summary
        typer.echo(f"\n📊 Trend Report - {report.time_period}")
        typer.echo(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        typer.echo(f"Report ID: {report.report_id}")
        
        typer.echo(f"\n🔥 Top Keywords ({len(report.top_keywords)}):")
        for i, trend in enumerate(report.top_keywords[:5], 1):
            typer.echo(f"   {i}. {trend.keyword} - {trend.score.current_score:.1f}")
        
        typer.echo(f"\n📈 Rising Trends ({len(report.rising_trends)}):")
        for i, trend in enumerate(report.rising_trends[:5], 1):
            typer.echo(f"   {i}. {trend.keyword} - +{trend.score.growth_rate:.1f}%")
        
        typer.echo(f"\n📊 Category Breakdown:")
        for category, count in list(report.category_breakdown.items())[:5]:
            category_name = category.value if hasattr(category, 'value') else str(category)
            typer.echo(f"   {category_name}: {count}")
        
        if report.key_insights:
            typer.echo(f"\n💡 Key Insights:")
            for insight in report.key_insights:
                typer.echo(f"   • {insight}")
        
        if report.content_opportunities:
            typer.echo(f"\n🎯 Content Opportunities:")
            for opportunity in report.content_opportunities:
                typer.echo(f"   • {opportunity}")
        
        # Save report if requested
        if output_file:
            report_data = {
                "report_id": report.report_id,
                "generated_at": report.generated_at.isoformat(),
                "time_period": report.time_period,
                "summary": {
                    "total_keywords": len(report.top_keywords),
                    "rising_trends": len(report.rising_trends),
                    "declining_trends": len(report.declining_trends)
                },
                "top_keywords": [{"keyword": t.keyword, "score": t.score.current_score} for t in report.top_keywords[:10]],
                "rising_trends": [{"keyword": t.keyword, "growth_rate": t.score.growth_rate} for t in report.rising_trends[:10]],
                "category_breakdown": {str(k): v for k, v in report.category_breakdown.items()},
                "insights": report.key_insights,
                "opportunities": report.content_opportunities,
                "recommended_keywords": report.recommended_keywords
            }
            
            output_path = Path(output_file)
            output_path.write_text(json.dumps(report_data, indent=2))
            typer.echo(f"\n💾 Full report saved to {output_path}")
        
    except Exception as e:
        typer.echo(f"❌ Error generating report: {e}")

@app.command()
def trend_stats():
    """Show trend database statistics."""
    try:
        scraper = TrendScraper()
        summary = scraper.get_trend_summary()
        
        typer.echo("📊 Trend Database Statistics:")
        typer.echo(f"   Total Keywords: {summary['database_stats']['total_keywords']}")
        typer.echo(f"   Total Reports: {summary['database_stats']['total_reports']}")
        typer.echo(f"   Account Profiles: {summary['database_stats']['account_profiles']}")
        typer.echo(f"   Categories Tracked: {summary['categories_tracked']}")
        
        if summary['database_stats']['avg_score'] > 0:
            typer.echo(f"   Average Score: {summary['database_stats']['avg_score']:.1f}")
        
        typer.echo(f"\n🔥 Top Keywords:")
        for i, keyword in enumerate(summary['top_keywords'][:5], 1):
            typer.echo(f"   {i}. {keyword}")
        
        typer.echo(f"\n📈 Rising Keywords:")
        for i, keyword in enumerate(summary['rising_keywords'][:5], 1):
            typer.echo(f"   {i}. {keyword}")
        
    except Exception as e:
        typer.echo(f"❌ Error getting trend stats: {e}")

@app.command()
def cleanup_trends(
    days: int = typer.Option(30, help="Remove trends older than N days"),
    confirm: bool = typer.Option(False, "--yes", help="Skip confirmation")
):
    """Clean up old trend data."""
    try:
        scraper = TrendScraper()
        
        if not confirm:
            typer.confirm(f"Remove trends older than {days} days?", abort=True)
        
        removed = scraper.cleanup_old_trends(days)
        typer.echo(f"✅ Cleaned up {removed} old trend records")
        
    except typer.Abort:
        typer.echo("Cleanup cancelled.")
    except Exception as e:
        typer.echo(f"❌ Error cleaning up trends: {e}")

@app.command()
def start_scheduler(
    data_dir: str = typer.Option("data/trends", help="Trend data directory"),
    daemon: bool = typer.Option(False, help="Run in background (daemon mode)")
):
    """Start the automated trend scheduler."""
    if daemon:
        typer.echo("❌ Daemon mode not implemented yet. Run without --daemon flag.")
        return
    
    typer.echo("🚀 Starting trend scheduler...")
    typer.echo("Press Ctrl+C to stop the scheduler")
    
    try:
        scheduler = TrendScheduler(data_dir)
        
        # Setup signal handling for graceful shutdown
        def signal_handler(signum, frame):
            typer.echo("\n🛑 Received shutdown signal, stopping scheduler...")
            scheduler.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run the scheduler
        asyncio.run(scheduler.run_scheduler_loop())
        
    except KeyboardInterrupt:
        typer.echo("\n✅ Scheduler stopped")
    except Exception as e:
        typer.echo(f"❌ Error running scheduler: {e}")

@app.command()
def scheduler_status():
    """Show status of all scheduled trend jobs."""
    try:
        scheduler = TrendScheduler()
        scheduler.start()
        
        status = scheduler.get_job_status()
        
        typer.echo("📅 Trend Scheduler Status:")
        typer.echo("=" * 50)
        
        for job_id, info in status.items():
            enabled_status = "✅ Enabled" if info['enabled'] else "❌ Disabled"
            typer.echo(f"\n🔹 {info['name']} ({job_id})")
            typer.echo(f"   Status: {enabled_status}")
            typer.echo(f"   Description: {info['description']}")
            
            if info['next_run']:
                next_run = info['next_run'][:19]  # Remove milliseconds
                typer.echo(f"   Next Run: {next_run}")
            else:
                typer.echo(f"   Next Run: Not scheduled")
            
            if info['last_run']:
                last_run = info['last_run'][:19]  # Remove milliseconds
                typer.echo(f"   Last Run: {last_run}")
                typer.echo(f"   Last Status: {info['status']}")
            else:
                typer.echo(f"   Last Run: Never")
        
        scheduler.stop()
        
    except Exception as e:
        typer.echo(f"❌ Error getting scheduler status: {e}")

@app.command()
def pause_schedule(job_id: str):
    """Pause a specific scheduled job."""
    try:
        scheduler = TrendScheduler()
        scheduler.start()
        
        # Check if job exists
        status = scheduler.get_job_status()
        if job_id not in status:
            typer.echo(f"❌ Job '{job_id}' not found")
            typer.echo(f"Available jobs: {', '.join(status.keys())}")
            scheduler.stop()
            return
        
        scheduler.pause_job(job_id)
        typer.echo(f"⏸️  Paused job: {job_id}")
        
        scheduler.stop()
        
    except Exception as e:
        typer.echo(f"❌ Error pausing job: {e}")

@app.command()
def resume_schedule(job_id: str):
    """Resume a paused scheduled job."""
    try:
        scheduler = TrendScheduler()
        scheduler.start()
        
        # Check if job exists
        status = scheduler.get_job_status()
        if job_id not in status:
            typer.echo(f"❌ Job '{job_id}' not found")
            typer.echo(f"Available jobs: {', '.join(status.keys())}")
            scheduler.stop()
            return
        
        scheduler.resume_job(job_id)
        typer.echo(f"▶️  Resumed job: {job_id}")
        
        scheduler.stop()
        
    except Exception as e:
        typer.echo(f"❌ Error resuming job: {e}")

@app.command()
def run_job(job_id: str):
    """Trigger a scheduled job to run immediately."""
    try:
        scheduler = TrendScheduler()
        scheduler.start()
        
        # Check if job exists
        status = scheduler.get_job_status()
        if job_id not in status:
            typer.echo(f"❌ Job '{job_id}' not found")
            typer.echo(f"Available jobs: {', '.join(status.keys())}")
            scheduler.stop()
            return
        
        scheduler.run_job_now(job_id)
        typer.echo(f"🚀 Triggered job: {job_id}")
        typer.echo("Check scheduler status to see execution results")
        
        scheduler.stop()
        
    except Exception as e:
        typer.echo(f"❌ Error triggering job: {e}")

if __name__ == "__main__":
    app()