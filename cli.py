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
import os
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
        auto_post: bool = typer.Option(False, "--auto-post", help="Automatically post to the platform")
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
        typer.echo(f"{action} {platform} content for account: {account.name}")
        factory = OutputFactory(account, offline=offline, platform=platform, auto_post=auto_post)
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

if __name__ == "__main__":
    app()