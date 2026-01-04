import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent

DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SIGN_BOX_DIR = PROJECT_DIR / "sing-box"
SIGN_BOX_DIR.mkdir(parents=True, exist_ok=True)

SINGBOX_CONFIG_PATH = SIGN_BOX_DIR / "config.json"
