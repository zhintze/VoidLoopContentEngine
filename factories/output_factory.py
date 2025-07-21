from http.cookiejar import debug
from pathlib import Path
from datetime import datetime

import export
from jinja2 import Template
from openai.types.chat import ChatCompletionMessageParam

from models.account import Account
import json


from template_loader import load_template_config


class OutputFactory:
    def __init__(self, account: Account,offline: bool = False):
        self.account = account
        self.offline = offline
        self.template_path = Path("templates") / f"{account.template_id}.j2"
        self.output_dir = Path("output") / datetime.now().strftime("%Y-%m-%d") / account.name
        self.template = load_template_config(account.template_id)

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

    def call_gpt(self, prompt: str) -> tuple[str, dict]:
        from openai import OpenAI
        import os
        import tiktoken

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = "gpt-4"
        encoding = tiktoken.encoding_for_model(model)

        prompt_tokens = len(encoding.encode(prompt))

        try:
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": "You are a helpful food blogger."},
                {"role": "user", "content": str(prompt)}
            ]
            response = client.chat.completions.create(
                model=self.template.model,
                messages=messages,
                temperature=self.template.temperature,
                max_tokens=1000,
            )
        except Exception as e:
            print("GPT call failed:")
            print(e)
            raise

        output_text = response.choices[0].message.content

        print("=== GPT Output Preview ===")
        print(output_text[:300])
        print("==========================")

        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens

        usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "model": model,
            "estimated_cost_usd": round((prompt_tokens * 0.01 + completion_tokens * 0.03) / 1000, 4)
        }

        return output_text, usage



    def format_output(self, gpt_output: str, usage: dict) -> dict:
        return {
            "markdown": f"# Blog Post\n\n{gpt_output}",
            "caption": f"{gpt_output[:150]}...",
            "debug": {
                "raw_output": gpt_output,
                "keywords": self.account.keywords,
                "tokens": usage
            }
        }

    def save_output(self, content: dict):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "blog.md").write_text(content["markdown"])

        (self.output_dir / "caption.txt").write_text(content["caption"])
        (self.output_dir / "debug.json").write_text(json.dumps(content["debug"], indent=2))

    def run(self):
        prompt = self.generate_prompt()
        if self.offline:
            print(" Offline mode enabled — skipping GPT call.")
            gpt_output = "[OFFLINE MODE] This is a placeholder output.\n\n" + prompt
            usage = {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": 0,
                "total_tokens": len(prompt.split()),
                "model": "offline",
                "estimated_cost_usd": 0.0
            }
        else:
            gpt_output, usage = self.call_gpt(prompt)
        formatted = self.format_output(gpt_output, usage)
        print("=== Saving output ===")
        print("MARKDOWN PREVIEW:")
        print(formatted["markdown"][:200])
        print("DEBUG PREVIEW:")
        print(json.dumps(formatted["debug"], indent=2)[:300])
        self.save_output(formatted)
        print(f"Output saved to {self.output_dir}")
