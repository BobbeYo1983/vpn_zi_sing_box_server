import json
import os
import subprocess
from core.paths import SINGBOX_CONFIG_PATH
from .models import VpnUser
from urllib.parse import quote

FLOW = "xtls-rprx-vision"
SERVER = os.environ["SINGBOX_SERVER"]
SERVER_PORT = int(os.environ["SERVER_PORT"])
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
                "listen": "85.198.90.103",
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

    SINGBOX_CONFIG_PATH.write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def build_vless_uri(user):
    return (
        f"vless://{user.uuid}@{SERVER}:{SERVER_PORT}"
        f"?encryption=none" 
        f"&security=reality"
        f"&fp=firefox"  
        f"&sni={SERVER_NAME}"
        f"&pbk={PUBLIC_KEY}"
        f"&sid={SHORT_ID}"
        f"&flow={FLOW}"
        f"&type=tcp"                
        f"#{quote(user.name)}"
    )