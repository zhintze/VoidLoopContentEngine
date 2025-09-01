from http.cookiejar import debug
from pathlib import Path
from datetime import datetime

from jinja2 import Template
from openai.types.chat import ChatCompletionMessageParam

from models.account import Account
import json
import os
from typing import Dict, Any

from template_loader import load_template_config
from services.instagram_api import InstagramAPIConfig
from services.pinterest_api import PinterestAPIConfig


class OutputFactory:
    def __init__(self, account: Account, offline: bool = False, platform: str = "blog", 
                 auto_post: bool = False):
        self.account = account
        self.offline = offline
        self.platform = platform
        self.auto_post = auto_post
        
        # Select template based on platform
        if platform == "instagram":
            template_id = f"{account.template_id}_instagram"
        elif platform == "pinterest":
            template_id = f"{account.template_id}_pinterest"
        else:
            template_id = account.template_id
            
        self.template_path = Path("templates") / f"{template_id}.j2"
        self.output_dir = Path("output") / datetime.now().strftime("%Y-%m-%d") / account.name
        self.template = load_template_config(template_id)
        
        # Initialize API clients if auto_post is enabled
        self.instagram_api = None
        self.pinterest_api = None
        if auto_post and not offline:
            # Try account-specific credentials first, fallback to env
            self.instagram_api = (InstagramAPIConfig.from_account(account) or 
                                  InstagramAPIConfig.from_env())
            self.pinterest_api = (PinterestAPIConfig.from_account(account) or 
                                  PinterestAPIConfig.from_env())

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
        if self.platform == "instagram":
            return {
                "instagram_caption": gpt_output,
                "image_description": self.generate_image_description(gpt_output),
                "debug": {
                    "raw_output": gpt_output,
                    "keywords": self.account.keywords,
                    "tokens": usage,
                    "platform": "instagram"
                }
            }
        elif self.platform == "pinterest":
            return {
                "pinterest_description": gpt_output,
                "pin_title": self.extract_pin_title(gpt_output),
                "image_description": self.generate_image_description(gpt_output),
                "debug": {
                    "raw_output": gpt_output,
                    "keywords": self.account.keywords,
                    "tokens": usage,
                    "platform": "pinterest"
                }
            }
        else:
            return {
                "markdown": f"# Blog Post\n\n{gpt_output}",
                "caption": f"{gpt_output[:150]}...",
                "debug": {
                    "raw_output": gpt_output,
                    "keywords": self.account.keywords,
                    "tokens": usage,
                    "platform": "blog"
                }
            }

    def generate_image_description(self, content: str) -> str:
        """Generate a description for the recipe image based on content"""
        # Extract recipe name if present
        lines = content.split('\n')
        recipe_name = "recipe dish"
        
        # Look for recipe name in first few lines
        for line in lines[:5]:
            if any(word in line.lower() for word in ["recipe", "dish", "meal"]):
                # Try to extract a food name
                words = line.split()
                for i, word in enumerate(words):
                    if word.lower() in ["recipe", "dish", "meal"] and i > 0:
                        recipe_name = " ".join(words[max(0, i-2):i])
                        break
                break
        
        return f"Overhead shot of delicious {recipe_name} in a rustic bowl, garnished and styled for food photography, warm natural lighting, kitchen background"

    def extract_pin_title(self, content: str) -> str:
        """Extract a Pinterest-friendly title from content"""
        lines = content.split('\n')
        first_line = lines[0].strip()
        
        # If first line looks like a title, use it
        if len(first_line) < 100 and any(keyword in first_line.lower() for keyword in self.account.keywords):
            return first_line
        
        # Otherwise create one from keywords
        primary_keyword = self.account.keywords[0] if self.account.keywords else "recipe"
        return f"{primary_keyword.title()} Recipe - Quick & Easy"

    def save_output(self, content: dict):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.platform == "instagram":
            (self.output_dir / "instagram_caption.txt").write_text(content["instagram_caption"])
            (self.output_dir / "image_description.txt").write_text(content["image_description"])
        elif self.platform == "pinterest":
            (self.output_dir / "pinterest_description.txt").write_text(content["pinterest_description"])
            (self.output_dir / "pin_title.txt").write_text(content["pin_title"])
            (self.output_dir / "image_description.txt").write_text(content["image_description"])
        else:
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
        
        # Platform-specific preview
        if self.platform == "instagram":
            print("INSTAGRAM CAPTION PREVIEW:")
            print(formatted["instagram_caption"][:200])
        elif self.platform == "pinterest":
            print("PINTEREST DESCRIPTION PREVIEW:")
            print(formatted["pinterest_description"][:200])
        else:
            print("MARKDOWN PREVIEW:")
            print(formatted["markdown"][:200])
            
        print("DEBUG PREVIEW:")
        print(json.dumps(formatted["debug"], indent=2)[:300])
        self.save_output(formatted)
        print(f"Output saved to {self.output_dir}")
        
        # Auto-post if enabled
        if self.auto_post and not self.offline:
            self.post_to_platform(formatted)

    def post_to_platform(self, content: Dict[str, Any]):
        """Post content to the specified platform"""
        print(f"\n=== Auto-posting to {self.platform.upper()} ===")
        
        if self.platform == "instagram":
            self.post_to_instagram(content)
        elif self.platform == "pinterest":
            self.post_to_pinterest(content)
        else:
            print("Auto-posting not supported for blog platform")

    def post_to_instagram(self, content: Dict[str, Any]):
        """Post to Instagram using the Graph API"""
        if not self.instagram_api:
            print("❌ Instagram API not configured")
            return
            
        # Get required data
        caption = content.get("instagram_caption", "")
        image_description = content.get("image_description", "")
        
        # For MVP, we need an image URL - this would typically come from:
        # 1. AI image generation service (DALL-E, Midjourney)
        # 2. Stock photo API
        # 3. Pre-uploaded image library
        
        # Get image URL from account or environment
        image_url = (self.account.api_credentials.default_image_url or 
                     os.getenv('DEFAULT_RECIPE_IMAGE_URL', 
                               'https://via.placeholder.com/1080x1080?text=Recipe+Image'))
        
        print(f"Caption: {caption[:100]}...")
        print(f"Image: {image_url}")
        
        success = self.instagram_api.post_image(image_url, caption)
        if success:
            print("✅ Successfully posted to Instagram!")
        else:
            print("❌ Failed to post to Instagram")

    def post_to_pinterest(self, content: Dict[str, Any]):
        """Post to Pinterest using the Pinterest API"""
        if not self.pinterest_api:
            print("❌ Pinterest API not configured")
            return
            
        # Get required data
        title = content.get("pin_title", "Recipe")
        description = content.get("pinterest_description", "")
        image_description = content.get("image_description", "")
        
        # Get board name from account or environment
        board_name = (self.account.api_credentials.pinterest_board_name or 
                      os.getenv('PINTEREST_BOARD_NAME', 'Recipes'))
        board_id = self.pinterest_api.find_board_by_name(board_name)
        
        if not board_id:
            print(f"❌ Pinterest board '{board_name}' not found")
            return
        
        # Get image URL from account or environment
        image_url = (self.account.api_credentials.default_image_url or 
                     os.getenv('DEFAULT_RECIPE_IMAGE_URL', 
                               'https://via.placeholder.com/1000x1500?text=Pinterest+Recipe'))
        
        # Optional: link back to blog
        blog_link = self.account.site if hasattr(self.account, 'site') else None
        
        print(f"Title: {title}")
        print(f"Description: {description[:100]}...")
        print(f"Board: {board_name} ({board_id})")
        print(f"Image: {image_url}")
        
        success = self.pinterest_api.post_pin(board_id, title, description, 
                                              image_url, blog_link)
        if success:
            print("✅ Successfully posted to Pinterest!")
        else:
            print("❌ Failed to post to Pinterest")
