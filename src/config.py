from pathlib import Path

import yaml

PROJECT_DIR = Path(__file__).resolve().parent.parent
RESOURCES_DIR = PROJECT_DIR / "resources"

_CONFIG_FILE = PROJECT_DIR / "config/config.yaml"
_SECRET_CONFIG_FILE = PROJECT_DIR / "secrets/config.yaml"

with _SECRET_CONFIG_FILE.open(encoding="utf-8") as f:
    secret_config = yaml.safe_load(f)

with _CONFIG_FILE.open(encoding="utf-8") as f:
    config = yaml.safe_load(f)
