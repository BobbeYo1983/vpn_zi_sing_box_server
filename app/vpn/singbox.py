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
    # 1️⃣ Формируем конфигурацию полностью,
    #    независимо от того, есть пользователи или нет
    config = {
        "log": {
            "level": "info"
        },
        "inbounds": [
            {
                "type": "vless",
                "tag": "vless-in",
                "listen": "0.0.0.0",
                "listen_port": SERVER_PORT,  # ОБЯЗАТЕЛЬНО int, не строка
                "users": build_users(),      # фильтр по enabled=True внутри
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

    # 2️⃣ ВАЖНО: атомарная запись
    #    Пишем сначала во временный файл рядом с основным
    tmp_path: Path = SINGBOX_CONFIG_PATH.with_suffix(".tmp")

    tmp_path.write_text(
        json.dumps(
            config,
            indent=2,
            ensure_ascii=False  # чтобы имена пользователей могли быть на русском
        ),
        encoding="utf-8"
    )

    # 3️⃣ АТОМАРНАЯ замена файла
    #    - гарантированно меняет inode
    #    - systemd path unit это УВИДИТ
    #    - файл никогда не бывает "наполовину записан"
    os.replace(tmp_path, SINGBOX_CONFIG_PATH)


def build_vless_uri(user):
    return (
        f"vless://{user.uuid}@{SERVER}:{SERVER_PORT}" #TODO сделать, чтобы автоматом брался IP
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