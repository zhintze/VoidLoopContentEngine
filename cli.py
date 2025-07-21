import typer
import toml
from pathlib import Path
from datetime import datetime
from models.account import Account

app = typer.Typer()

ACCOUNTS_DIR = Path("accounts")
SCHEDULE_FILE = Path("scheduler/schedule.toml")
OUTPUT_DIR = Path("output")

@app.command()
def new_account(
        name: str,
        site: str,
        instagram: str = "",
        pinterest: str = "",
        keywords: str = "",
        tone: str = "neutral",
        hashtags: str = ""
):
    """Create a new account TOML config."""
    account_path = ACCOUNTS_DIR / f"{name}.toml"
    data = {
        "name": name,
        "site": site,
        "social_handles": {
            "instagram": instagram,
            "pinterest": pinterest,
        },
        "keywords": keywords.split(","),
        "tone": tone,
        "hashtags": hashtags.split(","),
    }
    ACCOUNTS_DIR.mkdir(exist_ok=True)
    with open(account_path, "w") as f:
        toml.dump(data, f)
    typer.echo(f"✅ Created account: {account_path}")

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
def run_account(account_name: str):
    """Run the full content generation flow for a given account."""
    account_path = ACCOUNTS_DIR / f"{account_name}.toml"
    if not account_path.exists():
        typer.echo(f"Account file not found: {account_path}")
        raise typer.Exit(code=1)

    try:
        account = Account.from_toml(str(account_path))
        typer.echo(f"✅ Loaded account: {account.name}")
    except Exception as e:
        typer.echo(f"Failed to load account: {e}")
        raise typer.Exit(code=1)

    today = datetime.now().strftime("%Y-%m-%d")
    out_path = OUTPUT_DIR / today / account_name
    out_path.mkdir(parents=True, exist_ok=True)

    typer.echo(f" Would now generate content using template: {account.template_id}")
    typer.echo(f"📝 Would save output to: {out_path}")

if __name__ == "__main__":
    app()
