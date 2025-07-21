
from pathlib import Path
import toml
from models.template import Template

def load_template_config(template_id: str) -> Template:
    """
    Load the TOML config for a given template ID from templates/{template_id}.toml
    and return a validated Template object.
    """
    path = Path(f"templates/{template_id}.j2")
    if not path.exists():
        raise FileNotFoundError(f"Template config not found: {path}")

    data = toml.load(path)
    return Template(**data)
