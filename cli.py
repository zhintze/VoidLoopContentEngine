import typer
import toml
from pathlib import Path
from datetime import datetime
from models.account import Account
from factories.output_factory import OutputFactory
from dotenv import load_dotenv
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
        "template_id": template_id,  # default for now; consider making this a CLI option
        "site": site,
        "social_handles": {
            "instagram": instagram,
            "pinterest": pinterest,
        },
        "keywords": [kw.strip() for kw in keywords.split(",") if kw.strip()],
        "tone": tone,
        "hashtags": [ht.strip() for ht in hashtags.split(",") if ht.strip()],
        "outputs": [],
        "post_queue": [],
        "log_entries": [],
    }
    ACCOUNTS_DIR.mkdir(exist_ok=True)
    with open(account_path, "w") as f:
        toml.dump(data, f)
    typer.echo(f"Created account: {account_path}")

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
        offline: bool = typer.Option(False, "--offline", help="Run without calling the OpenAI API")
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
        typer.echo(f"testing account: {account.name}")
        factory = OutputFactory(account, offline=offline)  # pass flag
        factory.run()
    except Exception as e:
        typer.echo(f"Error during content generation: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
