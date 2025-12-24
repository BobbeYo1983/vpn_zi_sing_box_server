import json
import os
import subprocess
from pathlib import Path
from .models import VpnUser
from urllib.parse import quote
from core.paths import DATA_DIR

CONFIG_PATH = DATA_DIR / "singbox.json"
FLOW = "xtls-rprx-vision"
SERVER = os.environ["SINGBOX_SERVER"]
SERVER_PORT = os.environ["SERVER_PORT"]
SERVER_NAME = os.environ["SINGBOX_SERVER_NAME"]
PRIVATE_KEY = os.environ["SINGBOX_REALITY_PRIVATE_KEY"]
PUBLIC_KEY = os.environ["SINGBOX_REALITY_PUBLIC_KEY"]
SHORT_ID = os.environ["SINGBOX_SHORT_ID"]

def build_users():
    return [
        {
            "name": u.name,
            "uuid": str(u.uuid),
            "flow": FLOW,
        }
        for u in VpnUser.objects.filter(enabled=True)
    ]

def write_config():
    config = {
        "log": {
            "level": "info"
        },
        "inbounds": [
            {
                "type": "vless",
                "tag": "vless-in",
                "listen": "0.0.0.0",
                "listen_port": SERVER_PORT,
                "users": build_users(),
                "tls": {
                    "enabled": True,
                    "server_name": SERVER_NAME,
                    "reality": {
                        "enabled": True,
                        "handshake": {
                            "server": SERVER_NAME,
                            "server_port": 443
                        },
                        "private_key": PRIVATE_KEY,
                        "short_id": [SHORT_ID]
                    }
                }
            }
        ],
        "outbounds": [
            {
                "type": "direct",
                "tag": "direct"
            }
        ]
    }

    CONFIG_PATH.write_text(
        json.dumps(config, indent=2),
        encoding="utf-8"
    )

def check_config():
    subprocess.run(
        ["sing-box", "check", "-C", "/etc/sing-box/"],
        check=True
    )

def reload_singbox():
    subprocess.run(
        ["sudo", "systemctl", "reload", "sing-box"],
        check=True
    )

# def reload_singbox():
#     subprocess.run(
#         "pidof sing-box | xargs sudo kill -HUP",
#         shell=True,
#         check=True
#     )

def build_vless_uri(user):
    return (
        f"vless://{user.uuid}@{SERVER}:{SERVER_PORT}"
        f"?type=tcp"
        f"&security=reality"
        f"&flow={FLOW}"
        f"&sni={SERVER_NAME}"
        f"&fp=chrome"
        f"&pbk={PUBLIC_KEY}"
        f"&sid={SHORT_ID}"
        f"#{quote(user.name)}"
    )