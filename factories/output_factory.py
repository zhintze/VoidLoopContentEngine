
from pathlib import Path
from datetime import datetime
from jinja2 import Template
from models.account import Account
import json

class OutputFactory:
    def __init__(self, account: Account):
        self.account = account
        self.template_path = Path("templates") / f"{account.template_id}.j2"
        self.output_dir = Path("output") / datetime.now().strftime("%Y-%m-%d") / account.name

    def load_template(self) -> Template:
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        return Template(self.template_path.read_text())

    def generate_prompt(self) -> str:
        template = self.load_template()
        return template.render(
            keywords=self.account.keywords,
            tone=self.account.tone,
            hashtags=self.account.hashtags
        )

    def call_gpt(self, prompt: str) -> str:
        # Stub for now; replace with OpenAI call or other generator
        return f"[Mock GPT output based on prompt: {prompt}]"

    def format_output(self, gpt_output: str) -> dict:
        return {
            "markdown": f"# Blog Post\n\n{gpt_output}",
            "caption": f"{gpt_output[:150]}...",
            "debug": {
                "raw_output": gpt_output,
                "keywords": self.account.keywords
            }
        }

    def save_output(self, content: dict):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "blog.md").write_text(content["markdown"])
        (self.output_dir / "caption.txt").write_text(content["caption"])
        (self.output_dir / "debug.json").write_text(json.dumps(content["debug"], indent=2))

    def run(self):
        prompt = self.generate_prompt()
        gpt_output = self.call_gpt(prompt)
        formatted = self.format_output(gpt_output)
        self.save_output(formatted)
        print(f"✅ Output saved to {self.output_dir}")
