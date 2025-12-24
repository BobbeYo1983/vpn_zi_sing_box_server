import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SIGN_BOX_DIR = BASE_DIR / "sing-box"
SIGN_BOX_DIR.mkdir(parents=True, exist_ok=True)

SINGBOX_CONFIG_PATH = SIGN_BOX_DIR / "config.json"
