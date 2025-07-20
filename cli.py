# cli.py
import typer
import toml
from pathlib import Path

app = typer.Typer()

ACCOUNTS_DIR = Path("accounts")
SCHEDULE_FILE = Path("scheduler/schedule.toml")

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
    typer.echo(f"🗓️ Scheduled post for {account} on {day} at {time}")

if __name__ == "__main__":
    app()
